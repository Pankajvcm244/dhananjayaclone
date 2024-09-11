from frappe.desk.page.setup_wizard.setup_wizard import make_records

import frappe


def execute():
    for seva_type in frappe.get_all(
        "Seva Type", pluck="name", filters={"csr_allowed": 1}
    ):
        doc = frappe.get_doc("Seva Type", seva_type)
        doc.donation_type = "Both"
        doc.save()
