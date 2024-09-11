# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DonorClaimRequest(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        donor: DF.Link | None
        full_name: DF.Data | None
        patron: DF.Link | None
        patron_name: DF.Data | None
        preacher_claimed: DF.Link | None
        status: DF.Literal["Pending", "Approved", "Rejected"]
        user: DF.Link
    # end: auto-generated types
    def on_update(self):
        settings_doc = frappe.get_cached_doc("Dhananjaya Settings")
        if self.status == "Approved":
            doc = frappe.get_doc(
                {
                    "doctype": "App Notification",
                    "app": settings_doc.firebase_admin_app,
                    "channel": settings_doc.donor_claim_channel,
                    "user": self.user,
                    "subject": "Donor Claim Approved!",
                    "message": f"Your request to claim donor {self.full_name} is Approved. Please check the change.",
                    "is_route": 1,
                    "route": f"/donor/{self.donor}",
                }
            )
            doc.insert(ignore_permissions=True)
        elif self.status == "Rejected":
            doc = frappe.get_doc(
                {
                    "doctype": "App Notification",
                    "app": settings_doc.firebase_admin_app,
                    "channel": settings_doc.donor_claim_channel,
                    "user": self.user,
                    "subject": "Donor Claim Rejected!",
                    "message": f"Your request to claim donor {self.full_name} is Rejected. Please contact Admin for further discussion.",
                }
            )
            doc.insert(ignore_permissions=True)

        frappe.db.commit()


@frappe.whitelist()
def update_preacher(request, preacher):
    request = frappe.get_doc("Donor Claim Request", request)
    if request.donor:
        donor = frappe.get_doc("Donor", request.donor)
        donor.llp_preacher = preacher
        donor.save()
    if request.patron:
        patron = frappe.get_doc("Patron", request.patron)
        patron.llp_preacher = preacher
        patron.save()
