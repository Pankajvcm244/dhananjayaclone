# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import json
import tarfile
import zipfile, io
import random, string
from pytz import timezone
import boto3
from erpnext.support.doctype.service_level_agreement.service_level_agreement import (
    convert_utc_to_user_timezone,
)
import frappe, os
from frappe.boot import get_system_timezone
from frappe.utils import flt
from frappe.utils.background_jobs import is_job_enqueued
from frappe.model.document import Document

from dhananjaya.dhananjaya.utils import get_pdf_dr


class DhananjayaReceiptsExport(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        company: DF.Link
        date_from: DF.Date | None
        date_to: DF.Date | None
    # end: auto-generated types
    pass


@frappe.whitelist()
def get_backup_files():
    export_doc = frappe.get_doc("Dhananjaya Receipts Export")
    frappe.only_for(["System Manager", "DCC Manager"])
    files_path = []
    settings = frappe.get_single("Dhananjaya Settings")
    bucket_name = settings.re_bucket_name
    conn = boto3.client(
        "s3",
        aws_access_key_id=settings.re_access_key_id,
        aws_secret_access_key=settings.get_password("re_access_key_secret"),
        endpoint_url=settings.re_endpoint_url or "https://s3.amazonaws.com",
    )
    response = conn.list_objects_v2(Bucket=bucket_name, Prefix=f"{export_doc.company}/")
    files = response.get("Contents")
    if files:
        files = sorted(files, key=lambda x: x["LastModified"], reverse=True)
        system_tz = get_system_timezone()
        for file in files:
            modified_dt = file["LastModified"].astimezone(timezone(system_tz))
            file_download_link = f"https://{bucket_name}.s3.amazonaws.com/{file['Key']}"
            files_path.append(
                {
                    "name": file["Key"],
                    "size": flt(file["Size"] / (1024 * 1024), 2),
                    "last_modified": modified_dt.strftime("%d %b, %Y | %I:%M %p"),
                    "link": file_download_link,
                }
            )
    # frappe.errprint(files_path)
    return files_path


@frappe.whitelist()
def generate_receipts():
    export_doc = frappe.get_doc("Dhananjaya Receipts Export")

    conditions = ""

    conditions += f' AND tdr.receipt_date BETWEEN "{export_doc.date_from}" AND "{export_doc.date_to}"'

    conditions += f' AND tdr.company = "{export_doc.company}"'

    receipts = frappe.db.sql(
        f"""
        select *
        from `tabDonation Receipt` tdr
        where workflow_state = 'Realized' {conditions}
        order by receipt_date
        """,
        as_dict=1,
    )

    receipt_monthly_bundle = {}

    for r in receipts:
        month_year = f"""{r["receipt_date"].year}-{r["receipt_date"].month}"""
        if month_year not in receipt_monthly_bundle:
            receipt_monthly_bundle[month_year] = []
        receipt_monthly_bundle[month_year].append(r)

    for month_year, bundle in receipt_monthly_bundle.items():
        backup_file_name_prefix = month_year
        job_id = f"receipts_export::{export_doc.company}::{month_year}"
        if not is_job_enqueued(job_id):
            frappe.enqueue(
                process_receipts_pdf_bundle,
                queue="long",
                timeout=10800,
                company=export_doc.company,
                job_id=job_id,
                receipts=[receipt["name"] for receipt in bundle],
                backup_file_name_prefix=backup_file_name_prefix,
            )


def delete_local_file_post_upload_(prefix):
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


def process_receipts_pdf_bundle(company, receipts, backup_file_name_prefix):
    setup_backup_directory()
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
    folder_file_name = f"{company}/{file_name}"

    upload_file_to_s3(folder_file_name, receipts_file_path)
    delete_local_file_post_upload_(backup_file_name_prefix)


# def demo():
#     filename = "Hare Krishna Movement Jaipur-2024-4-xirpoy.tar"
#     filepath = "./hkmjerp.in/public/receipts_backup/Hare Krishna Movement Jaipur-2024-4-xirpoy.tar"
#     upload_file_to_s3(filename,filepath)


def upload_file_to_s3(filename, filepath):
    settings = frappe.get_single("Dhananjaya Settings")
    conn = boto3.client(
        "s3",
        aws_access_key_id=settings.re_access_key_id,
        aws_secret_access_key=settings.get_password("re_access_key_secret"),
        endpoint_url=settings.re_endpoint_url or "https://s3.amazonaws.com",
    )
    bucket = settings.re_bucket_name
    try:
        print(f"Uploading file: {filename}")
        conn.upload_file(filepath, bucket, filename)  # Requires PutObject permission

    except Exception as e:
        frappe.log_error()
        print(f"Error uploading: {e}")
