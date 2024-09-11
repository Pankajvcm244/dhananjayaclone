from dhananjaya.dhananjaya.report.upcoming_patron_pujas.patron_puja_calculator import (
    get_patron_puja_dates,
)
from dhananjaya.dhananjaya.utils import get_credits_equivalent, get_preachers
from dhananjaya.dhananjaya.report.upcoming_special_pujas.puja_calculator import (
    get_puja_dates,
)
from frappe.utils.data import getdate
import frappe
from datetime import datetime, time


@frappe.whitelist()
def get_events_calendar(from_date, to_date):
    from_date = getdate(from_date)
    to_date = getdate(to_date)
    preachers = get_preachers()
    special_pujas = get_puja_dates(from_date, to_date, preachers)
    for puja in special_pujas:
        puja["event_id"] = puja.pop("puja_id")
        puja["event"] = puja.pop("occasion")
        puja["event_type"] = "Special Puja"
        puja["date"] = datetime.combine(puja["date"], time.min)
        puja["all_day"] = 1
    priviledge_pujas = get_patron_puja_dates(from_date, to_date, preachers)
    for puja in priviledge_pujas:
        puja["event_id"] = puja.pop("puja_id")
        puja["event"] = puja.pop("occasion")
        puja["event_type"] = "Privilege Puja"
        puja["date"] = datetime.combine(puja["date"], time.min)
        puja["all_day"] = 1

    reminders = get_reminder_list(from_date, to_date)

    for reminder in reminders:
        reminder["event_type"] = "Donor Reminder"
        reminder["all_day"] = 0

    events = special_pujas + priviledge_pujas + reminders

    events = sorted(events, key=lambda x: x["date"])
    return events


def get_reminder_list(from_date, to_date):
    return frappe.db.get_all(
        "DJ Reminder",
        filters=[
            ["user", "=", frappe.session.user],
            ["remind_at", "between", [from_date, to_date]],
        ],
        fields=[
            "name AS event_id",
            "message AS event",
            "donor",
            "donor_name",
            "user",
            "remind_at AS date",
        ],
    )
