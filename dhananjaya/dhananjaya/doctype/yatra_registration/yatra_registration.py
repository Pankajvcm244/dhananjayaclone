# Copyright (c) 2024, Narahari Dasa and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document


class YatraRegistration(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        adult_seats: DF.Int
        amended_from: DF.Link | None
        children_seats: DF.Int
        donor: DF.Link | None
        donor_creation_request: DF.Link | None
        donor_name: DF.Data | None
        from_date: DF.Date | None
        preacher: DF.Link
        seva_subtype: DF.Link
        to_date: DF.Date | None
        total_cost: DF.Currency
    # end: auto-generated types

    def before_save(self):
        sevasubtype_doc = frappe.get_doc("Seva Subtype", self.seva_subtype)
        self.total_cost = (
            self.adult_seats * sevasubtype_doc.adult_cost
            + self.children_seats * sevasubtype_doc.child_cost
        )
        if self.donor:
            self.donor_name = frappe.get_value("Donor", self.donor, "full_name")
        elif self.donor_creation_request:
            self.donor_name = frappe.get_value(
                "Donor Creation Request", self.donor_creation_request, "full_name"
            )
        else:
            frappe.throw("At least one of Donor or Donor Creation Request is required")
