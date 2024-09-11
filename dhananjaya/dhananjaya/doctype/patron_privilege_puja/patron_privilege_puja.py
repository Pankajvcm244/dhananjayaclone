# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PatronPrivilegePuja(Document):
    def before_insert(self):
        self.validate_count()

    def validate_count(self):
        exisiting = frappe.db.count(
            "Patron Privilege Puja", filters={"patron": self.patron}
        )
        patron_seva_type = frappe.db.get_value("Patron", self.patron, "seva_type")
        if patron_seva_type is None:
            frappe.throw("Please set the seva type in Patron Document.")
        allowed = frappe.db.get_value(
            "Patron Seva Type", patron_seva_type, "privilege_pujas"
        )
        if allowed <= exisiting:
            frappe.throw(f"Patron Priviledge Seva limit crossed. Limit : {allowed}")
        return
