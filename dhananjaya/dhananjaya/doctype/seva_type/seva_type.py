# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

from dhananjaya.dhananjaya.doctype.dhananjaya_notifier.dhananjaya_notifier import (
    generate_version,
)
import frappe
from frappe.model.document import Document


class SevaType(Document):
    @property
    def csr_separate_accounting(self):
        return frappe.db.get_single_value(
            "Dhananjaya Settings", "separate_accounting_for_csr"
        )

    def autoname(self):
        self.name = get_abbreviated_name(self.seva_name, self.company)

    def before_rename(self, old, new, merge=False):
        # renaming consistency with abbreviation
        if not frappe.get_cached_value("Company", self.company, "abbr") in new:
            new = get_abbreviated_name(new, self.company)
        return new

    def on_change(self):
        generate_version(self.doctype)

    def on_update(self):
        self.delete_box_key()

    def on_trash(self):
        self.delete_box_key()

    def delete_box_key(self):
        frappe.cache().hdel("dhananjaya_box", "seva_type")


def get_abbreviated_name(name, company):
    abbr = frappe.get_cached_value("Company", company, "abbr")
    new_name = "{0} - {1}".format(name, abbr)
    return new_name


@frappe.whitelist()
def get_cached_documents():
    seva_types = frappe.cache().hget("dhananjaya_box", "seva_type") or frappe._dict()
    if not seva_types:
        seva_types = frappe.get_all(
            "Seva Type", fields=["*"], filters={"enabled": 1}, order_by="priority desc"
        )
        frappe.cache().hset("dhananjaya_box", "seva_type", seva_types)
    return seva_types
