from frappe.desk.page.setup_wizard.setup_wizard import make_records
import frappe


def execute():
    tokens = frappe.get_all("Firebase App Token", pluck="name")
    for t in tokens:
        frappe.delete_doc("Firebase App Token", t)
    frappe.db.commit()
