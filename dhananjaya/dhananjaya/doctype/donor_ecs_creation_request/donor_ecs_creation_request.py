# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class DonorECSCreationRequest(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        account_bank_name: DF.Data
        account_holder_name: DF.Data
        account_number: DF.Data
        amount: DF.Currency
        company: DF.Link
        company_abbreviation: DF.Data | None
        debit_pay_on: DF.Literal["7", "14", "21"]
        donor: DF.Link
        donor_name: DF.Data | None
        end_date: DF.Date
        frequency: DF.Literal["Yearly", "Half Yearly", "Quarterly", "Monthly"]
        naming_series: DF.Literal[".company_abbreviation.EC.YY.1.#####"]
        patron: DF.Link | None
        patron_name: DF.Data | None
        payment_mode: DF.Literal["Debit Card", "Internet Banking"]
        seva_type: DF.Link | None
        start_date: DF.Date
        status: DF.Literal["Pending", "Completed", "Rejected"]

    # end: auto-generated types
    def on_change(self):
        if self.has_value_changed("status"):
            self.notify_mobile_app_users()
            if self.status == "Completed":
                self.update_donor_ecs_details()

    #######################################################

    def notify_mobile_app_users(self):
        message = title = None
        current_time = datetime.now().strftime("%d %B, %Y %I:%M %p")
        if self.status == "Completed":
            title = f"ECS Request Completed!"
            message = f"ECS Request {self.name} of {self.account_holder_name} is completed. Sit back & relax to observe auto-generation of receipts."

        elif self.status == "Rejected":
            title = f"ECS Request Rejected!"
            message = f"ECS Request {self.name} of {self.account_holder_name} is rejected. Please contact Administrator for resolution."

        # IF Message is Ready!
        if title is not None:
            erp_users = [self.owner]
            settings_doc = frappe.get_cached_doc("Dhananjaya Settings")
            for erp_user in erp_users:
                doc = frappe.get_doc(
                    {
                        "doctype": "App Notification",
                        "app": settings_doc.firebase_admin_app,
                        "channel": settings_doc.ecs_channel,
                        "user": erp_user,
                        "subject": title,
                        "message": message,
                    }
                )
                doc.insert(ignore_permissions=True)

    ##########################################################

    def update_donor_ecs_details(self):
        settings_doc = frappe.get_cached_doc("Dhananjaya Settings")
        frappe.set_value(
            "Donor",
            self.donor,
            {
                "ecs_active": 1,
                "ecs_bank": settings_doc.default_ecs_bank,
                "bank": self.account_bank_name,
                "ecs_bank_ac_no": self.account_number,
                "account_holder": self.account_holder_name,
                "ecs_id": self.name,
                "opening_date": self.start_date,
                "closing_date": self.end_date,
                "ecs_amount": self.amount,
                "settlement_day": self.debit_pay_on,
                "periodicity": self.frequency[0].upper(),
                "ecs_default_seva_type": self.seva_type,
                "ecs_default_patron": self.patron,
            },
        )
