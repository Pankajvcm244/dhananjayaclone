import frappe
from dhananjaya.dhananjaya.utils import (
    get_short_url,
    get_preachers,
    encode_donation_id,
    download_pdf,
    download_pdf_public,
)


@frappe.whitelist()
def stct_get_short_url(long_url):
    return get_short_url(long_url)


@frappe.whitelist()
def stct_get_preachers():
    return get_preachers()


@frappe.whitelist()
def stct_encode_donation_id(receiptId):
    return encode_donation_id(receiptId)


@frappe.whitelist()
def stct_encode_donation_id(receiptId):
    return encode_donation_id(receiptId)


@frappe.whitelist()
def stct_download_pdf(name):
    return download_pdf(name)


@frappe.whitelist(allow_guest=True)
def stct_download_pdf_public(receiptToken):
    return download_pdf_public(
        receiptToken,
        doctype="Donation Receipt",
    )
