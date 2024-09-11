# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from dhananjaya.dhananjaya.doctype.dhananjaya_notifier.dhananjaya_notifier import (
    generate_version,
)
from frappe.model.document import Document


class DJPaymentDetail(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        account_no: DF.Data | None
        bank: DF.Data | None
        branch: DF.Data | None
        document_attachment: DF.Attach | None
        document_name: DF.Data | None
        gateway_image: DF.AttachImage | None
        gateway_message: DF.LongText | None
        gateway_name: DF.Data | None
        ifsc_code: DF.Data | None
        name: DF.Int | None
        title: DF.Data | None
        trust: DF.Link
        type: DF.Literal["Account", "UPI", "Gateway", "Document"]
        upi: DF.Data | None
        upi_qr_image: DF.AttachImage | None
    # end: auto-generated types
    def on_change(self):
        generate_version(self.doctype)

    def on_update(self):
        self.delete_box_key()

    def on_trash(self):
        self.delete_box_key()

    def delete_box_key(self):
        frappe.cache().hdel("dhananjaya_box", "dj_payment_detail")


@frappe.whitelist()
def get_cached_documents():
    payment_details = (
        frappe.cache().hget("dhananjaya_box", "dj_payment_detail") or frappe._dict()
    )
    if not payment_details:
        payment_details = frappe.get_all("DJ Payment Detail", fields=["*"])
        frappe.cache().hset("dhananjaya_box", "dj_payment_detail", payment_details)
    return payment_details
