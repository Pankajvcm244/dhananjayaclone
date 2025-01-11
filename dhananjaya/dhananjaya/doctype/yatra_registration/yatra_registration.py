# Copyright (c) 2024, Narahari Dasa and contributors
# For license information, please see license.txt

# import frappe
from hmac import new
import frappe
from frappe.model import document
from frappe.model.document import Document


class YatraRegistration(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from dhananjaya.dhananjaya.doctype.registration_seat_detail.registration_seat_detail import RegistrationSeatDetail
        from dhananjaya.dhananjaya.doctype.yatra_participant_details.yatra_participant_details import YatraParticipantDetails
        from frappe.types import DF

        amended_from: DF.Link | None
        donor: DF.Link | None
        donor_creation_request: DF.Link | None
        donor_name: DF.Data | None
        from_date: DF.Date | None
        participants: DF.Table[YatraParticipantDetails]
        preacher: DF.Link | None
        received_amount: DF.Currency
        seats: DF.Table[RegistrationSeatDetail]
        seva_subtype: DF.Link
        to_date: DF.Date | None
        total_cost: DF.Currency
    # end: auto-generated types

    @property
    def received_amount(self):
        return frappe.db.sql(
            f'SELECT IFNULL( SUM(amount), 0 ) FROM `tabDonation Receipt` WHERE workflow_state = \'Realized\' AND seva_subtype = "{self.seva_subtype}" AND yatra_registration = "{self.name}"'
        )[0][0]

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
            frappe.throw(f"Duplicates Entry Not Allowed")

    def validate_seats(self):
        proper_seats = [s for s in self.seats if s.count != 0]
        if not proper_seats:
            frappe.throw("At least one seat is required")
        self.seats = proper_seats

    def validate_participants(self):
        seats = sum(s.count for s in self.seats if s.count != 0)
        if len(self.participants) > seats:
           return frappe.throw("Passenger count cannot be greater than seats")
    def validate(self):
        self.validate_donor()
        self.validate_duplicate()
        self.validate_seats()
        seats_map = self.get_seats_map()
        self.validate_participants()

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
                        tyr.seva_subtype = '{self.seva_subtype.replace("'", "''")}'
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

    def on_submit(self):
        seats = sum(s.count for s in self.seats if s.count != 0)
        if len(self.participants) > seats:
           return frappe.throw("Passenger count cannot be greater than seats")
        proper_seats = [s for s in self.seats if s.count != 0]

        if not proper_seats:
            frappe.throw("At least one seat is required")

        self.seats = proper_seats
    def before_update_after_submit(self):
        document = frappe.get_doc(
            "Yatra Registration", self.name
        )
        previous_seats_map = {seat.seat_type: seat.count for seat in document.seats}
        new_seats_map = {seat.seat_type: seat.count for seat in self.seats}
        for i in self.seats:
            new_seats_map[i.seat_type] = i.count
        for seat, new_count in new_seats_map.items():
            previous_count = previous_seats_map.get(seat, 0)
            if new_count <= previous_count:
                continue
            extra_new_seats = new_count - previous_count
            get_available_seats(self.seva_subtype  , seat , extra_new_seats)
        if len(self.participants or []) > sum(s.count for s in self.seats if s.count != 0):
           return frappe.throw("Passenger count cannot be greater than seats") 
       
def get_available_seats(seva_subtype , seat , count):
      seats_map = get_seats_map(seva_subtype)
      booked_seats = frappe.db.sql(
          f"""SELECT 
                  ifnull(sum(`count`),0)
              FROM `tabRegistration Seat Detail` trsd
              JOIN `tabYatra Registration` tyr
                  ON tyr.name = trsd.parent
              WHERE
                  tyr.seva_subtype = '{seva_subtype.replace("'", "''")}'
                  AND tyr.docstatus = 1
                  AND trsd.seat_type = '{seat}' """,
      )[0][0]
      if (booked_seats + count) > seats_map[seat].count:
                frappe.throw(
                    f"Only {seats_map[seat].count - booked_seats} for category : {seat} are available for {seva_subtype}"
                ) 
      
      return              
    
    
def get_seats_map(seva_subtype):
        sevasubtype_doc = frappe.get_doc("Seva Subtype", seva_subtype)
        seats_map = {}
        for s in sevasubtype_doc.seats:
            seats_map[s.seat_type] = frappe._dict(count=s.count, cost=s.cost)
        return seats_map        