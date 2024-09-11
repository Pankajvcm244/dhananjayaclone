from frappe.desk.page.setup_wizard.setup_wizard import make_records
import frappe


def execute():
    records = [
        {
            "doctype": "OAuth Client",
            "app_name": "Dhananjaya",
            "skip_authorization": 1,
            "default_redirect_uri": "in.hkmjerp.dhananjaya",
            "scopes": "all",
            "redirect_uris": "in.hkmjerp.dhananjaya://callback",
            "grant_type": "Authorization Code",
            "response_type": "Code",
        }
    ]
    exisiting_apps = frappe.get_all(
        "OAuth Client",
        filters={
            "app_name": "Dhananjaya",
        },
        pluck="name",
    )
    if len(exisiting_apps) == 0:
        make_records(records)
