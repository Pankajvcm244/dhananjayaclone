import frappe
from frappe import _
from dhananjaya.dhananjaya.doctype.donation_receipt.constants import (
    CASH_PAYMENT_MODE,
    TDS_PAYMENT_MODE,
    PAYMENT_GATWEWAY_MODE,
    CHEQUE_MODE,
)
from dhananjaya.dhananjaya.utils import (
    get_best_contact_address,
    get_company_defaults,
    get_pdf_dr,
    get_preacher_users,
)


def validate_govt_laws(doc):
    if isinstance(doc.amount, str):
        doc.amount = float(doc.amount)
    day_donation = get_donation_of_the_day(doc)
    if (
        doc.payment_method == CASH_PAYMENT_MODE
        and (doc.amount + day_donation) >= 200000
    ):
        frappe.throw(
            "On the same day, Cash Donations <b>>= 2 Lacs</b> are not allowed."
        )
    elif (
        doc.payment_method == CASH_PAYMENT_MODE
        and not doc.flags.kyc_available
        and (doc.amount + day_donation) >= 52000
    ):
        frappe.throw(
            f"""On the same day, a single donor cannot contribute <b>>= 52000</b> in cash mode with <b>NO KYC</b> available."""
        )
    elif (
        doc.payment_method == CASH_PAYMENT_MODE
        and (doc.amount + day_donation) >= 200000
    ):
        frappe.throw(
            "On the same day, a Donor cannot contribute cash <b>>= 2,00,000</b>"
        )
    return


def get_donation_of_the_day(doc):
    total_donation = 0
    con_str = (
        f" donor = '{doc.donor}' "
        if doc.donor
        else f" donor_creation_request = '{doc.donor_creation_request}' "
    )
    qr = frappe.db.sql(
        f"""
            SELECT SUM(amount) 
            FROM `tabDonation Receipt` 
            WHERE {con_str}
            AND payment_method = '{doc.payment_method}' 
            AND receipt_date = '{doc.receipt_date}'
            AND docstatus != 2
            AND company = '{doc.company}'
            AND name != '{doc.name}'
            """
    )
    if qr[0][0]:
        total_donation = qr[0][0]
    return int(total_donation)


def validate_donor(doc):
    if not (doc.donor or doc.donor_creation_request):
        frappe.throw("At Least one of Donor or Donor Creation Request is required.")
    return
def validate_yatra_required(doc):
    if frappe.db.get_value("Seva Subtype", doc.seva_subtype, "is_a_yatra") and not doc.yatra_registration:
        frappe.throw("Yatra Registration is required.")

    return

def validate_cheque_screenshot(doc):
    if doc.payment_method == CHEQUE_MODE and not doc.payment_screenshot:
        frappe.throw("Cheque's Screenshot is required.")
    return


def validate_reference_number(doc):
    if not (doc.remarks or doc.payment_method in [CASH_PAYMENT_MODE, CHEQUE_MODE]):
        frappe.throw(
            "Reference Number is compulsory in case of non-Cash/Cheque Receipts."
        )
    return


def validate_kind_donation(doc):
    is_kind_mode = doc.is_kind_donation()
    sevatype_kind = frappe.db.get_value("Seva Type", doc.seva_type, "kind")
    if is_kind_mode and (not sevatype_kind):
        frappe.throw(
            "Please select a Seva Type of In-Kind Donation, since the Mode is Kind Donation"
        )

    if is_kind_mode and (not doc.kind_type):
        frappe.throw("Please select a type of Kind Donation")
    return


def validate_cheque_details(doc):
    if doc.payment_method == CHEQUE_MODE:
        if not doc.cheque_number:
            frappe.throw("Cheque Number is required")
        if not doc.cheque_date:
            frappe.throw("Cheque Date is required")
    return


def validate_donation_account(doc):
    ## Check if Donation Account is set where Credit will happend in JE
    if not doc.donation_account:
        frappe.throw(_("Income account for Donation is <b>NOT</b> set."))


def validate_modes_account(doc):
    ## CHECK WHETHER REQUIRED ACCOUNTS ARE SET
    if doc.is_kind_donation():
        return
    elif doc.payment_method == CASH_PAYMENT_MODE:
        if not doc.cash_account:
            frappe.throw(_("Cash Account is not provided."))
    elif doc.payment_method == TDS_PAYMENT_MODE:
        if not doc.tds_account:
            frappe.throw(_("TDS Account is not provided."))
    else:
        if not doc.bank_account:
            frappe.throw(_("Bank Account is not provided."))
        if not doc.bank_transaction:
            frappe.throw(
                _("Bank Transaction is required to be linked before realisation.")
            )
    return


def validate_atg_required(doc):
    if not doc.flags.kyc_available and doc.atg_required:
        frappe.throw(
            "At least one of the KYC ( PAN Number or Aadhar Number) is required for 80G Donation."
        )
    return
