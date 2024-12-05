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
        from dhananjaya.dhananjaya.doctype.registration_seat_detail.registration_seat_detail import RegistrationSeatDetail
        from frappe.types import DF

        amended_from: DF.Link | None
        donor: DF.Link | None
        donor_creation_request: DF.Link | None
        donor_name: DF.Data | None
        from_date: DF.Date | None
        preacher: DF.Link | None
        seats: DF.Table[RegistrationSeatDetail]
        seva_subtype: DF.Link
        to_date: DF.Date | None
        total_cost: DF.Currency
    # end: auto-generated types

    def get_seats_map(self):
        sevasubtype_doc = frappe.get_doc("Seva Subtype", self.seva_subtype)
        seats_map = {}
        for s in sevasubtype_doc.seats:
            seats_map[s.seat_type] = frappe._dict(count=s.count, cost=s.cost)
        return seats_map

    def validate_donor(self):
        if self.donor:
            self.donor_name, self.preacher = frappe.get_value(
                "Donor", self.donor, ["full_name", "llp_preacher"]
            )

        elif self.donor_creation_request:
            self.donor_name, self.preacher = frappe.get_value(
                "Donor Creation Request",
                self.donor_creation_request,
                ["full_name", "llp_preacher"],
            )
        else:
            frappe.throw("At least one of Donor or Donor Creation Request is required")

    
    def validate_duplicate(self):
        seat = [i.seat_type for i in self.seats]
        duplicates = set([s for s in seat if seat.count(s) > 1])
        if duplicates:
            frappe.throw(
                f"Duplicates Entry Not Allowed"
            )
    
    def validate(self):
        self.validate_donor()
        self.validate_duplicate()
        seats_map = self.get_seats_map()
        total_amount = 0
        for rs in self.seats:
            if rs.seat_type not in seats_map:
                frappe.throw(
                    f"Seat Type : {rs.seat_type} is not available for {self.seva_subtype}"
                )
            total_amount = total_amount + rs.count * seats_map[rs.seat_type].cost

            booked_seats = frappe.db.sql(
                f"""SELECT 
                        ifnull(sum(`count`),0)
                    FROM `tabRegistration Seat Detail` trsd
                    JOIN `tabYatra Registration` tyr
                        ON tyr.name = trsd.parent
                    WHERE
                        tyr.seva_subtype = '{self.seva_subtype}'
                        AND tyr.docstatus = 1
                        AND trsd.seat_type = '{rs.seat_type}' """,
            )[0][0]

            if (booked_seats + rs.count) > seats_map[rs.seat_type].count:
                frappe.throw(
                    f"Only {seats_map[rs.seat_type].count - booked_seats} for category : {rs.seat_type} are available for {self.seva_subtype}"
                )
        self.total_cost = total_amount
        return

    def on_cancel(self):
        for d in frappe.get_all(
            "Donation Receipt",
            filters={"yatra_registration": self.name},
            pluck="name",
        ):
            frappe.db.set_value("Donation Receipt", d, "yatra_registration", None)
