# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DJDocument(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        attachment: DF.Attach
        company: DF.Link
        title: DF.Data
        type: DF.Literal["General", "Patron"]
    # end: auto-generated types

    def on_update(self):
        self.delete_box_key()

    def on_trash(self):
        self.delete_box_key()

    def delete_box_key(self):
        frappe.cache().hdel("dhananjaya_box", "dj_document")


@frappe.whitelist()
def get_cached_documents():
    documents = frappe.cache().hget("dhananjaya_box", "dj_document") or frappe._dict()
    if not documents:
        documents = frappe.get_all("DJ Document", fields=["*"])
        frappe.cache().hset("dhananjaya_box", "dj_document", documents)
    return documents
