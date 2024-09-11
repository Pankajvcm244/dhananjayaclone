# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
import os
from frappe import _
from frappe.model.document import Document
from frappe.utils.xlsxutils import (
    read_xls_file_from_attached_file,
    read_xlsx_file_from_attached_file,
)
from frappe.utils.csvutils import get_csv_content_from_google_sheets, read_csv_content

STANDARD_FIELDS = ["transaction_id", "amount", "fee"]


class PGUploadTool(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        company: DF.Link
        gateway: DF.Link
        gateway_file: DF.Attach | None
        google_sheets_url: DF.Data | None

    # end: auto-generated types
    def get_data_from_template_file(self):
        content = None
        extension = None

        if self.gateway_file:
            content, extension = self.read_file(self.gateway_file)

        elif self.google_sheets_url:
            content = get_csv_content_from_google_sheets(self.google_sheets_url)
            extension = "csv"

        if not content:
            frappe.throw(_("Invalid or corrupted content for import"))

        if not extension:
            extension = "csv"

        if content:
            return self.read_content(content, extension)

    def read_content(self, content, extension):
        error_title = _("Template Error")
        if extension not in ("csv", "xlsx", "xls"):
            frappe.throw(
                _("Import template should be of type .csv, .xlsx or .xls"),
                title=error_title,
            )

        if extension == "csv":
            data = read_csv_content(content)
        elif extension == "xlsx":
            data = read_xlsx_file_from_attached_file(fcontent=content)
        elif extension == "xls":
            data = read_xls_file_from_attached_file(content)

        return data

    def read_file(self, file_path: str):
        extn = os.path.splitext(file_path)[1][1:]

        file_content = None

        file_name = frappe.db.get_value("File", {"file_url": file_path})
        if file_name:
            file = frappe.get_doc("File", file_name)
            file_content = file.get_content()

        return file_content, extn


def get_standard_indices(headers):
    std_indices_pos = {}
    for field in STANDARD_FIELDS:
        if field in headers:
            std_indices_pos.setdefault(field, headers.index(field))
        else:
            frappe.throw("Standard Fields are not in Uploaded File.")
    return std_indices_pos


@frappe.whitelist()
def upload_gateway_transactions(*args, **kwargs):
    pg_upload_tool = frappe.get_cached_doc("PG Upload Tool")
    rows = pg_upload_tool.get_data_from_template_file()
    count = 0

    # Get Index of Transaction ID
    headers = rows[0]
    std_indices = get_standard_indices(rows[0])

    # Batch Details Capture
    batch_doc = frappe.new_doc("PG Upload Batch")
    batch_doc.company = pg_upload_tool.company
    batch_doc.gateway = pg_upload_tool.gateway
    batch_doc.insert()

    total_amount, total_fee = 0, 0

    for row in rows[1:]:
        data = {
            "doctype": "Payment Gateway Transaction",
            "gateway": pg_upload_tool.gateway,
            "company": pg_upload_tool.company,
        }
        for field in STANDARD_FIELDS:
            data.setdefault(field, row[std_indices[field]])
        extra_data = {}
        for idx, header in enumerate(headers):
            if header not in STANDARD_FIELDS:
                extra_data[header] = row[idx]
        data.setdefault("extra_data", extra_data)
        if data["transaction_id"] is not None:
            doc = frappe.get_doc(data)
            doc.batch = batch_doc.name
            doc.insert()
            total_amount += float(doc.amount)
            total_fee += float(doc.fee)

    batch_doc.total_amount = total_amount
    batch_doc.total_fee = total_fee
    batch_doc.batch_amount = total_amount - total_fee
    batch_doc.remaining_amount = total_amount - total_fee
    batch_doc.save()
    frappe.db.commit()
