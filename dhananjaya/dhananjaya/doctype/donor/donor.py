# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

from dhananjaya.dhananjaya.doctype.donor.ecs_utils import count_of_ecs, get_ecs_months
import frappe
import re
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import strip, sbool
from frappe.model.document import Document

from dhananjaya.dhananjaya.utils import (
    get_preacher_users,
    is_valid_aadhar_number,
    is_valid_pan_number,
    is_valid_pincode,
    sanitise_str,
)


class Donor(Document):
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
        from dhananjaya.dhananjaya.doctype.special_puja_detail.special_puja_detail import (
            SpecialPujaDetail,
        )
        from frappe.types import DF

        aadhar_no: DF.Data | None
        account_holder: DF.Data | None
        addresses: DF.Table[DonorAddress]
        ashraya_level: DF.Literal["", "20", "16", "12", "8", "4", "1"]
        bank: DF.Data | None
        closing_date: DF.Date | None
        contacts: DF.Table[DonorContact]
        date_of_birth: DF.Date | None
        donor_creation_request: DF.Link | None
        driving_license: DF.Data | None
        ecs_active: DF.Check
        ecs_amount: DF.Currency
        ecs_bank: DF.Link | None
        ecs_bank_ac_no: DF.Data | None
        ecs_default_patron: DF.Link | None
        ecs_default_seva_type: DF.Link | None
        ecs_id: DF.Data | None
        ecs_type: DF.Literal["Physical Mandate", "E-NACH"]
        emails: DF.Table[DonorEmail]
        first_name: DF.Data
        full_name: DF.Data | None
        ifsc_code: DF.Data | None
        introducer_preacher: DF.Data | None
        last_donation: DF.Date | None
        last_name: DF.Data | None
        llp_preacher: DF.Link
        months_to_apply: DF.Data | None
        naming_series: DF.Literal["DNR-.YYYY.-"]
        number_of_ecs: DF.Data | None
        occupation: DF.Data | None
        old_donor_id: DF.Data | None
        old_trust_code: DF.Int
        opening_date: DF.Date | None
        pan_no: DF.Data | None
        passport: DF.Data | None
        periodicity: DF.Literal["Y", "H", "Q", "M"]
        profile_image: DF.AttachImage | None
        puja_details: DF.Table[SpecialPujaDetail]
        remarks: DF.Data | None
        salutation: DF.Link | None
        settlement_day: DF.Literal["7", "14", "21"]
        spouse_name: DF.Data | None
        times_donated: DF.Int
        total_donated: DF.Currency
        unresolved_fax_column: DF.Data | None

    # end: auto-generated types
    def after_insert(self):
        if self.donor_creation_request:
            frappe.db.set_value(
                "Donor Creation Request",
                self.donor_creation_request,
                "status",
                "Closed",
            )
            donations = frappe.get_all(
                "Donation Receipt",
                filters={"donor_creation_request": self.donor_creation_request},
                pluck="name",
            )
            for d in donations:
                frappe.db.set_value(
                    "Donation Receipt",
                    d,
                    {
                        "donor": self.name,
                        "full_name": self.full_name,
                        "preacher": self.llp_preacher,
                    },
                )
            frappe.db.commit()
            self.notify_mobile_app_users_of_donor_creation()

    def notify_mobile_app_users_of_donor_creation(self):
        title = "Donor Created!"
        message = f"Your donor {self.full_name} has been created"
        data = {"route": "true", "target_route": f"/donor/{self.name}"}
        # erp_user = frappe.db.get_value("LLP Preacher", self.llp_preacher, "erp_user")
        erp_users = get_preacher_users(self.llp_preacher)
        settings_doc = frappe.get_cached_doc("Dhananjaya Settings")
        for erp_user in erp_users:
            doc = frappe.get_doc(
                {
                    "doctype": "App Notification",
                    "app": settings_doc.firebase_admin_app,
                    "channel": settings_doc.donor_creation_channel,
                    "user": erp_user,
                    "subject": title,
                    "message": message,
                    "is_route": 1,
                    "route": f"/donor/{self.name}",
                }
            )
            doc.insert(ignore_permissions=True)

    def validate(self):
        pass
        # self.validate_address()
        # self.validate_contact()
        # self.validate_email()
        # self.validate_kyc()

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

    def validate_address(self):
        # types = []   # We will no more have this validation.
        preferred_flag = False
        for i, address in enumerate(self.addresses):
            if address.preferred and preferred_flag:
                frappe.throw(_("Only one address can be set Preferred."))
            if address.preferred:
                preferred_flag = True
            if (strip(address.pin_code) != "") and (
                not is_valid_pincode(address.pin_code)
            ):
                frappe.throw(_(f"Row #{i+1} contains an invalid PIN Code."))
            # if address.type in types:
            # 	frappe.throw(_(f"Row #{i+1} is a <b>Duplicate</b> of address type {address.type}. Please remove it."))
            # types.append(address.type)
        return

    def validate_contact(self):
        contact_numbers = []
        for i, contact in enumerate(self.contacts):
            if contact.contact_no in contact_numbers:
                frappe.throw(
                    _(
                        f"Row #{i+1} is a <b>Duplicate</b> of contact_no number {contact.contact_no}. Please remove it."
                    )
                )
            contact_numbers.append(contact.contact_no)
        return

    def validate_email(self):
        emails = []
        for i, email in enumerate(self.emails):
            if email.email in emails:
                frappe.throw(
                    _(
                        f"Row #{i+1} is a <b>Duplicate</b> of email {email.email}. Please remove it."
                    )
                )
            emails.append(email.email)

    def validate_kyc(self):
        if self.pan_no:
            self.pan_no = re.sub(r"\s+", "", self.pan_no)
            if not is_valid_pan_number(self.pan_no):
                frappe.throw("PAN Number is Invalid.")

        if self.aadhar_no:
            self.aadhar_no = re.sub(r"\s+", "", self.aadhar_no)
            if not is_valid_aadhar_number(self.aadhar_no):
                frappe.throw("Aadhar Number is Invalid.")
        return

    @property
    def months_to_apply(self):
        if self.opening_date and self.periodicity:
            months = get_ecs_months(self.opening_date, self.periodicity)
            return ", ".join(months.values())
        return "NA"

    @property
    def number_of_ecs(self):
        if self.opening_date and self.periodicity and self.closing_date:
            return count_of_ecs(self.opening_date, self.periodicity, self.closing_date)
        return "NA"


@frappe.whitelist()
def create_patron_from_donor(source_name, target_doc=None, args=None):
    doclist = get_mapped_doc(
        "Donor",
        source_name,
        {
            "Donor": {
                "doctype": "Patron",
            }
        },
        target_doc,
    )
    return doclist
