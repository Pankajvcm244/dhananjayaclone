# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import tarfile
import zipfile, io
import random, string
import frappe, os
from frappe.utils.background_jobs import is_job_enqueued
from frappe.model.document import Document

from dhananjaya.dhananjaya.utils import get_pdf_dr


class DhananjayaReceiptsExport(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        based_on: DF.Literal["Receipt Date", "Realization Date"]
        company: DF.Link
        date_from: DF.Date | None
        date_to: DF.Date | None
    # end: auto-generated types
    pass


@frappe.whitelist()
def get_backup_files():
    frappe.only_for(["System Manager", "DCC Manager"])
    receipts_file_path = frappe.utils.get_site_path(f"public/receipts_backup")
    files_path = []
    if os.path.exists(receipts_file_path):
        file_list = os.listdir(receipts_file_path)
        for this_file in file_list:
            file_download_link = (
                frappe.utils.get_url() + f"/receipts_backup/{this_file}"
            )
            files_path.append({"name": this_file, "link": file_download_link})
    return files_path


@frappe.whitelist()
def generate_receipts():
    export_doc = frappe.get_doc("Dhananjaya Receipts Export")
    based_on_date = (
        "realization_date"
        if export_doc.based_on == "Realization Date"
        else "receipt_date"
    )

    conditions = ""

    if based_on_date == "realization_date":
        rd_condition = f""" 
                tdr.realization_date BETWEEN "{export_doc.date_from}" AND "{export_doc.date_to}"
                OR (
                    tdr.realization_date IS NULL 
                    AND 
                        tdr.receipt_date
                        BETWEEN 
                        "{export_doc.date_from}" 
                        AND "{export_doc.date_to}"
                    )
                """
        conditions += f" AND ({rd_condition})"
    else:
        conditions += f' AND tdr.{based_on_date} BETWEEN "{export_doc.date_from}" AND "{export_doc.date_to}"'

    conditions += f' AND tdr.company = "{export_doc.company}"'

    receipts = frappe.db.sql(
        f"""
        select *
        from `tabDonation Receipt` tdr
        where docstatus = 1 {conditions}
        order by {based_on_date}
        """,
        as_dict=1,
    )

    receipt_monthly_bundle = {}

    for r in receipts:
        month_year = f"{r[based_on_date].year}-{r[based_on_date].month}"
        if month_year not in receipt_monthly_bundle:
            receipt_monthly_bundle[month_year] = []
        receipt_monthly_bundle[month_year].append(r)

    for month_year, bundle in receipt_monthly_bundle.items():
        backup_file_name_prefix = export_doc.company + "-" + month_year
        job_id = f"receipts_export::{export_doc.company}::{month_year}"
        if not is_job_enqueued(job_id):
            frappe.enqueue(
                process_receipts_pdf_bundle,
                queue="long",
                timeout=10800,
                job_id=job_id,
                receipts=[receipt["name"] for receipt in bundle],
                backup_file_name_prefix=backup_file_name_prefix,
            )


def delete_old_backup(prefix):
    """
    Cleans up the backup_link_path directory by deleting older file
    """
    receipts_file_path = frappe.utils.get_site_path(f"public/receipts_backup")
    if os.path.exists(receipts_file_path):
        matching_files = [
            file for file in os.listdir(receipts_file_path) if file.startswith(prefix)
        ]
        for file in matching_files:
            file_path = os.path.join(receipts_file_path, file)
            os.remove(file_path)


def setup_backup_directory():
    receipts_folder = frappe.utils.get_site_path("public/receipts_backup")
    if not os.path.exists(receipts_folder):
        os.makedirs(receipts_folder, exist_ok=True)


def process_receipts_pdf_bundle(receipts, backup_file_name_prefix):
    setup_backup_directory()
    delete_old_backup(backup_file_name_prefix)

    pdf_bytes_list = []
    pdf_names = []

    for receipt_name in receipts:
        receipt = get_pdf_dr(doctype="Donation Receipt", name=receipt_name)
        pdf_bytes_list.append(receipt)
        pdf_names.append(receipt_name)

    letters = string.ascii_lowercase
    random_string = "".join(random.choice(letters) for i in range(6))

    file_name = f"{backup_file_name_prefix}-{random_string}.tar"
    receipts_file_path = frappe.utils.get_site_path(
        f"public/receipts_backup/{file_name}"
    )
    tar_data = io.BytesIO()
    with tarfile.open(fileobj=tar_data, mode="w|") as tar:
        for i, pdf_bytes in enumerate(pdf_bytes_list):
            tarinfo = tarfile.TarInfo(f"{pdf_names[i]}.pdf")
            tarinfo.size = len(pdf_bytes)
            tar.addfile(tarinfo=tarinfo, fileobj=io.BytesIO(pdf_bytes))
    tar_data.seek(0)

    with open(receipts_file_path, "wb") as file:
        file.write(tar_data.getvalue())
