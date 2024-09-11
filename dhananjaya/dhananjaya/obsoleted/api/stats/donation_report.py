import frappe
from datetime import datetime, date
from dhananjaya.dhananjaya.report.donation_cumulative_report.donation_cumulative_report import (
    execute as donation_cummulative_report,
)


@frappe.whitelist()
def execute():
    today_date_string = datetime.now().strftime("%Y-%m-%d")
    first_day_of_month = date.today().replace(day=1)
    first_day_of_month_string = first_day_of_month.strftime("%Y-%m-%d")
    filters = {"from_date": first_day_of_month, "to_date": today_date_string}
    return donation_cummulative_report(filters)
