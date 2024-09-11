import frappe
from dhananjaya.dhananjaya.utils import get_preachers


@frappe.whitelist()
def preachers():
    return get_preachers()


@frappe.whitelist(allow_guest=True)
def get_erp_domains():
    return frappe.get_all(
        "ERP Domain",
        filters=[["active", "=", 1]],
        fields=["name", "erp_title", "erp_address"],
        order_by="name asc",
    )
