from erpnext.accounts.general_ledger import make_gl_entries, make_reverse_gl_entries
import frappe
from dhananjaya.dhananjaya.doctype.donation_receipt.constants import (
    CASH_PAYMENT_MODE,
    TDS_PAYMENT_MODE,
    PAYMENT_GATWEWAY_MODE,
    CHEQUE_MODE,
)

from dhananjaya.dhananjaya.doctype.donation_receipt.donation_receipt import (
    add_payment_entry,
)
from dhananjaya.dhananjaya.doctype.pg_upload_batch.pg_upload_batch import (
    refresh_pg_upload_batch,
)
from frappe.model.docstatus import DocStatus


@frappe.whitelist()
def get_festival_benefit(request):
    request = frappe.get_doc("Donation Receipt", request)

    donation_dict = {
        "donation_receipt": request.name,
        "donor": request.donor,
        "donor_name": request.full_name,
        "donation_amount": request.amount,
        "receipt_date": request.receipt_date,
        "preacher": request.preacher,
    }
    benefit_entry = frappe.new_doc("Donor Festival Benefit")
    benefit_entry.update(donation_dict)
    # donor_entry.set("accounts", accounts)
    return benefit_entry


########################################
####### Cheque Bounce Procedure#########
########################################


@frappe.whitelist()
def receipt_bounce_operations(receipt):
    # Check for Permissions
    frappe.only_for(["DCC Executive", "DCC Manager"])

    #########################

    receipt_doc = frappe.get_doc("Donation Receipt", receipt)

    if receipt_doc.payment_method != CHEQUE_MODE:
        frappe.throw("Only allowed for Cheque")

    if receipt_doc.docstatus != 1 or not receipt_doc.bounce_transaction:
        frappe.throw("Bounced Transaction is Required for Realised Receipts.")

    forward_bank_tx_doc = frappe.get_doc(
        "Bank Transaction", receipt_doc.bank_transaction
    )
    reverse_bank_tx_doc = frappe.get_doc(
        "Bank Transaction", receipt_doc.bounce_transaction
    )

    forward_company_account = frappe.db.get_value(
        "Bank Account", forward_bank_tx_doc.bank_account, "account"
    )

    reverse_company_account = frappe.db.get_value(
        "Bank Account", reverse_bank_tx_doc.bank_account, "account"
    )

    gl_base_entries = [
        frappe._dict(
            posting_date=reverse_bank_tx_doc.date,
            account=receipt_doc.donation_account,
            debit=receipt_doc.amount,
            party_type="Donor",
            party=receipt_doc.donor,
        ),
        frappe._dict(
            posting_date=reverse_bank_tx_doc.date,
            account=reverse_company_account,
            credit=receipt_doc.amount,
        ),
    ]
    gl_entries = []
    for gb in gl_base_entries:
        gl_entries.append(
            receipt_doc.get_gl_dict(
                {
                    **gb,
                    **{
                        "cost_center": receipt_doc.cost_center,
                        "project": receipt_doc.project,
                    },
                },
                item=receipt_doc,
            )
        )
    make_gl_entries(gl_entries, merge_entries=False)
    voucher = {
        "payment_doctype": receipt_doc.doctype,
        "payment_name": receipt_doc.name,
        "amount": receipt_doc.amount,
    }
    add_payment_entry(reverse_bank_tx_doc, voucher)
    # Finally Cash Return Donation Receipt
    receipt_doc.db_set("workflow_state", "Bounced")


########################################
####### Cash Return Procedure ##########
########################################
@frappe.whitelist()
def receipt_cash_return_operations(receipt, cash_return_date):
    # Check for Permissions

    frappe.only_for("DCC Cashier")

    #########################

    receipt_doc = frappe.get_doc("Donation Receipt", receipt)

    if receipt_doc.payment_method != CASH_PAYMENT_MODE:
        frappe.throw("Only Cash receipts are allowed.")

    gl_base_entries = [
        frappe._dict(
            posting_date=cash_return_date,
            account=receipt_doc.donation_account,
            debit=receipt_doc.amount,
            party_type="Donor",
            party=receipt_doc.donor,
        ),
        frappe._dict(
            posting_date=cash_return_date,
            account=receipt_doc.cash_account,
            credit=receipt_doc.amount,
        ),
    ]
    gl_entries = []
    for gb in gl_base_entries:
        gl_entries.append(
            receipt_doc.get_gl_dict(
                {
                    **gb,
                    **{
                        "cost_center": receipt_doc.cost_center,
                        "project": receipt_doc.project,
                    },
                },
                item=receipt_doc,
            )
        )
    make_gl_entries(gl_entries, merge_entries=False)
    # Finally Cash Return Donation Receipt
    receipt_doc.db_set("workflow_state", "Cash Returned")
