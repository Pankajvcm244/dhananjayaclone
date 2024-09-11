from datetime import date
import frappe
from dhananjaya.dhananjaya.doctype.donor_suggestion.constants import MONTHS

today = date.today()


def create_donor_suggestions():
    donor_suggestions = {}
    settings = frappe.get_doc("Donor Suggestion Settings")
    for i in frappe.db.sql(
        f"""
			select td.name, td.last_donation, GROUP_CONCAT(DISTINCT  YEAR(tdr.receipt_date)) as years
			from `tabDonor` td
			join `tabDonation Receipt` tdr
			on tdr.donor = td.name
			where tdr.docstatus = 1 and MONTHNAME(tdr.receipt_date) = MONTHNAME(NOW())
			group by td.name
			""",
        as_dict=1,
    ):
        donor_suggestions.setdefault(
            i["name"],
            {
                "remarks": f"Donated in years {i['years']} in this same month.",
                "priority": 2,
            },
        )

    for i in frappe.db.sql(
        f"""
			select td.name, count(tdr.name) as times
			from `tabDonor` td
			join `tabDonation Receipt` tdr
			on tdr.donor = td.name
			where tdr.docstatus = 1 and tdr.receipt_date >= DATE_SUB(NOW(), INTERVAL 7 MONTH)
			group by td.name
			having count(tdr.name) >= {settings.six_months_frequency}
			""",
        as_dict=1,
    ):
        donor_suggestions.setdefault(
            i["name"],
            {
                "remarks": f"Donated {i['times']} times in last 6 months.",
                "priority": 3,
            },
        )

    for i in frappe.db.sql(
        f"""
			select td.name, td.last_donation
			from `tabDonor` td
			join `tabDonation Receipt` tdr
			on tdr.donor = td.name
			where td.last_donation is not null
			group by td.name
			having MIN(tdr.receipt_date) >= DATE_SUB(NOW(), INTERVAL 7 MONTH) AND MIN(tdr.receipt_date) <= DATE_SUB(NOW(), INTERVAL 1 MONTH)
			""",
        as_dict=1,
    ):
        donor_suggestions.setdefault(
            i["name"],
            {
                "remarks": f"New Donor in last 6 months.",
                "priority": 1,
            },
        )

    for s in donor_suggestions:
        set_donor_suggestion(
            s, donor_suggestions[s]["remarks"], donor_suggestions[s]["priority"]
        )

    frappe.db.commit()


def set_donor_suggestion(donor, remarks, priority):
    suggestions = frappe.get_all("Donor Suggestion", filters={"donor": donor})
    if len(suggestions) != 0:
        suggestion_doc = frappe.get_doc("Donor Suggestion", suggestions[0]["name"])
    else:
        suggestion_doc = frappe.new_doc("Donor Suggestion")
        suggestion_doc.donor = donor
        suggestion_doc.suggestion_month = today.strftime("%B")
        suggestion_doc.suggestion_year = today.year
        suggestion_doc.remarks = remarks
        suggestion_doc.priority = priority
        suggestion_doc.insert(ignore_permissions=True)
        return

    if (
        MONTHS[suggestion_doc.suggestion_month] < today.month
        and not suggestion_doc.disabled
        and priority > suggestion_doc.priority
    ):
        suggestion_doc.suggestion_month = today.strftime("%B")
        suggestion_doc.suggestion_year = today.strftime("%Y")
        suggestion_doc.remarks = remarks
        suggestion_doc.priority = priority
        suggestion_doc.save(ignore_permissions=True)
