from datetime import datetime, timedelta
from dhananjaya.dhananjaya.report.upcoming_patron_pujas.patron_puja_calculator import (
    get_patron_puja_dates,
)
import frappe
from dhananjaya.dhananjaya.utils import get_preachers
from dhananjaya.dhananjaya.report.upcoming_special_pujas.puja_calculator import (
    get_puja_dates,
)


def special_puja_notify():
    current_date = datetime.now().date()
    tomorrow = current_date + timedelta(days=1)
    users = []
    for i in frappe.db.sql(
        """
                    select user
                    from `tabLLP Preacher User`
                    where 1
                    group by user
                    """,
        as_dict=1,
    ):
        users.append(i["user"])
    for u in users:
        preachers = get_preachers(u)
        for puja in get_puja_dates(tomorrow, tomorrow, preachers):
            settings_doc = frappe.get_cached_doc("Dhananjaya Settings")
            doc = frappe.get_doc(
                {
                    "doctype": "App Notification",
                    "app": settings_doc.firebase_admin_app,
                    "channel": settings_doc.event_reminder_channel,
                    "user": u,
                    "subject": puja["occasion"],
                    "message": f"Special Puja Tomorrow for {puja['donor_name']}",
                    "is_route": 1,
                    "route": f"/donor/{puja['donor_id']}",
                }
            )
            doc.insert(ignore_permissions=True)
    frappe.db.commit()


def privilege_puja_notify():
    current_date = datetime.now().date()
    tomorrow = current_date + timedelta(days=1)
    users = []
    for i in frappe.db.sql(
        """
                    select user
                    from `tabLLP Preacher User`
                    where 1
                    group by user
                    """,
        as_dict=1,
    ):
        users.append(i["user"])
    for u in users:
        preachers = get_preachers(u)
        for puja in get_patron_puja_dates(tomorrow, tomorrow, preachers):
            settings_doc = frappe.get_cached_doc("Dhananjaya Settings")
            doc = frappe.get_doc(
                {
                    "doctype": "App Notification",
                    "app": settings_doc.firebase_admin_app,
                    "channel": settings_doc.event_reminder_channel,
                    "user": u,
                    "subject": puja["occasion"],
                    "message": f"Privilege Puja Tomorrow for {puja['patron_name']}",
                    "is_route": 1,
                    "route": f"/patron/{puja['patron_id']}",
                }
            )
            doc.insert(ignore_permissions=True)
    frappe.db.commit()
