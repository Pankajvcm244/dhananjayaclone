# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.data import cint

from dhananjaya.dhananjaya.utils import (
    get_credit_values,
    get_credits_equivalent,
    sanitise_str,
)


class Patron(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from dhananjaya.dhananjaya.doctype.donor_address.donor_address import (
            DonorAddress,
        )
        from dhananjaya.dhananjaya.doctype.donor_contact.donor_contact import (
            DonorContact,
        )
        from dhananjaya.dhananjaya.doctype.donor_email.donor_email import DonorEmail
        from dhananjaya.dhananjaya.doctype.patron_card_detail.patron_card_detail import (
            PatronCardDetail,
        )
        from dhananjaya.dhananjaya.doctype.patron_display_name.patron_display_name import (
            PatronDisplayName,
        )
        from dhananjaya.dhananjaya.doctype.patron_gift_issue.patron_gift_issue import (
            PatronGiftIssue,
        )
        from frappe.types import DF

        aadhar_no: DF.Data | None
        addresses: DF.Table[DonorAddress]
        card_valid_from: DF.Date | None
        cards: DF.Table[PatronCardDetail]
        committed_amount: DF.Currency
        contacts: DF.Table[DonorContact]
        date_of_birth: DF.Date | None
        display_names: DF.Table[PatronDisplayName]
        driving_license: DF.Data | None
        emails: DF.Table[DonorEmail]
        enrolled_date: DF.Date | None
        first_name: DF.Data
        full_name: DF.Data | None
        gifts: DF.Table[PatronGiftIssue]
        issued_card_no: DF.Data | None
        last_donation: DF.Date | None
        last_name: DF.Data | None
        latest_donation: DF.Currency
        llp_preacher: DF.Link
        naming_series: DF.Literal["PTR-.YYYY.-"]
        occupation: DF.Data | None
        old_patron_id: DF.Data | None
        old_patron_number: DF.Data | None
        old_trust_code: DF.Int
        pan_no: DF.Data | None
        passport: DF.Data | None
        patron_card_sr: DF.Data | None
        profile_image: DF.AttachImage | None
        salutation: DF.Link | None
        seva_type: DF.Link
        spouse_name: DF.Data | None
        times_donated: DF.Int
        total_donated: DF.Currency
        unresolved_fax_column: DF.Data | None

    # end: auto-generated types
    def validate(self):
        self.validate_display_names()
        self.validate_commitment_amount()

    def validate_display_names(self):
        allowed = frappe.get_value(
            "Dhananjaya Settings", "Dhananjaya Settings", "display_names_allowed"
        )
        if len(self.display_names) > cint(allowed):
            frappe.throw(f"Only {allowed} names are allowed.")

    def validate_commitment_amount(self):
        seva_amount = frappe.db.get_value(
            "Patron Seva Type", self.seva_type, "seva_amount"
        )
        if self.committed_amount < seva_amount:
            frappe.throw(
                "Commitment Amount of Patron can not be less than Seva Amount defined in Patronship Level."
            )
        return

    def before_save(self):
        # Preacher Change
        if (
            not self.is_new()
            and self.has_value_changed("llp_preacher")
            and "DCC Manager" not in frappe.get_roles()
        ):
            frappe.throw(
                "Only DCC Manager is allowed to change the Preacher of a Donor."
            )

        ####
        self.first_name = sanitise_str(self.first_name)
        self.full_name = self.first_name
        if self.last_name is not None:
            self.last_name = sanitise_str(self.last_name)
            self.full_name += " " + self.last_name
        return

    @property
    def total_donation(self):
        donations = frappe.db.get_all(
            "Donation Receipt",
            filters={"workflow_state": "Realized", "patron": self.name},
            pluck="amount",
        )
        return sum(donations)

    @property
    def total_credits_donation(self):
        total_donation = 0
        credits = frappe.db.get_all(
            "Donation Credit",
            filters={"patron": self.name},
            fields=["company", "credits"],
        )
        credit_values_map = get_credit_values()
        for credit_doc in credits:
            total_donation += (
                credit_values_map[credit_doc["company"]] * credit_doc["credits"]
            )
        return total_donation

    @property
    def commitment(self):
        if self.seva_type is None:
            return 0
        return frappe.db.get_value("Patron Seva Type", self.seva_type, "seva_amount")


@frappe.whitelist()
def get_patron_status(patron):
    doc = frappe.get_doc("Patron", patron)
    credits = doc.total_credits_donation
    return frappe._dict(
        completed=doc.total_donation + credits, commited=doc.commitment, credits=credits
    )
