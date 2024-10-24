# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PatronPrivilegePuja(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        day: DF.Literal["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31"]
        month: DF.Literal["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        naming_series: DF.Literal["PPP-.YY.-1.####"]
        occasion: DF.Data
        patron: DF.Link
        patron_name: DF.Data | None
        preacher: DF.Link | None
    # end: auto-generated types
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
