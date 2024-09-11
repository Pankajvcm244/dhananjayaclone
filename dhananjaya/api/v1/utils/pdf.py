from dhananjaya.dhananjaya.utils import (
    get_short_url,
    get_preachers,
    encode_donation_id,
    download_pdf,
    download_pdf_public,
)
import frappe


@frappe.whitelist()
def short_url(long_url):
    return get_short_url(long_url)


@frappe.whitelist()
def encode(receiptId):
    return encode_donation_id(receiptId)


@frappe.whitelist()
def download(name):
    return download_pdf(name)


@frappe.whitelist(allow_guest=True)
def download_public(receiptToken):
    return download_pdf_public(
        receiptToken,
        doctype="Donation Receipt",
    )
