# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import random_string


class DhananjayaNotifier(Document):
    def before_save(self):
        if not self.version:
            self.version = random_string(6)


def generate_version(doctype):
    if not frappe.db.exists("Dhananjaya Notifier", doctype):
        notify_doc = frappe.get_doc(
            {"doctype": "Dhananjaya Notifier", "doc_type": doctype}
        )
    else:
        notify_doc = frappe.get_doc("Dhananjaya Notifier", doctype)
    notify_doc.version = random_string(6)
    notify_doc.save(ignore_permissions=True)
