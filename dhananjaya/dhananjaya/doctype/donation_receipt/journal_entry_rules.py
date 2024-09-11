from dhananjaya.constants import DCC_EXCLUDE_ROLES
import frappe


def before_cancel(doc, method=None):
    if doc.donation_receipt:
        frappe.only_for(["DCC Executive", "DCC Manager"])
