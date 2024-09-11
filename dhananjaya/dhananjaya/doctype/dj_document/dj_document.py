# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DJDocument(Document):

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
