# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DJReminder(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        donor: DF.Link | None
        donor_name: DF.Data | None
        message: DF.Text
        remind_at: DF.Datetime
        user: DF.Link
    # end: auto-generated types
    pass


def show_reminders():
    settings_doc = frappe.get_cached_doc("Dhananjaya Settings")
    for i in frappe.db.sql(
        """
                    select *
                    from `tabDJ Reminder`
                    where DATE_FORMAT(remind_at, '%Y-%m-%d %H:%i') = DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i')
                    """,
        as_dict=1,
    ):
        doc = frappe.get_doc(
            {
                "doctype": "App Notification",
                "app": settings_doc.firebase_admin_app,
                "channel": settings_doc.event_reminder_channel,
                "user": i["user"],
                "subject": "Reminder",
                "message": i["message"],
                "is_route": 1 if i["donor"] else 0,
                "route": f"/donor/{i['donor']}",
            }
        )
        doc.insert(ignore_permissions=True)
    frappe.db.commit()
