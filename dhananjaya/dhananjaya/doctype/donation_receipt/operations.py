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

    if receipt_doc.docstatus == 1:
        if not receipt_doc.bounce_transaction:
            frappe.throw("Bounced Transaction is Required for Realised Receipts.")

        je = frappe.get_all(
            "Journal Entry",
            fields="name",
            filters={"donation_receipt": receipt_doc.name, "docstatus": 1},
        )

        if len(je) != 1:
            frappe.throw("There is no JE associated or are more than one entry.")
        je = je[0]
        je_dict = frappe.get_doc("Journal Entry", je["name"]).as_dict()
        forward_bank_tx_doc = frappe.get_doc(
            "Bank Transaction", receipt_doc.bank_transaction
        )
        reverse_bank_tx_doc = frappe.get_doc(
            "Bank Transaction", receipt_doc.bounce_transaction
        )

        transaction_amount = je_dict["total_debit"]

        forward_company_account = frappe.db.get_value(
            "Bank Account", forward_bank_tx_doc.bank_account, "account"
        )

        reverse_company_account = frappe.db.get_value(
            "Bank Account", reverse_bank_tx_doc.bank_account, "account"
        )

        for a in je_dict["accounts"]:
            if a["debit"] == 0:
                a["debit"] = transaction_amount
                a["debit_in_account_currency"] = transaction_amount
                a["credit"] = 0
                a["credit_in_account_currency"] = 0
            elif a["credit"] == 0:
                a["credit"] = transaction_amount
                a["credit_in_account_currency"] = transaction_amount
                a["debit"] = 0
                a["debit_in_account_currency"] = 0

            if a["account"] == forward_company_account:
                a["account"] = reverse_company_account

        del je_dict["clearance_date"]
        del je_dict["bank_statement_name"]
        del je_dict["name"]

        je_dict["posting_date"] = reverse_bank_tx_doc.date
        je_dict["user_remark"] = je_dict["user_remark"].replace(
            "BEING AMOUNT RECEIVED", "BEING AMOUNT RETURNED"
        )

        reverse_je = frappe.get_doc(je_dict)
        reverse_je.submit()
        voucher = {
            "payment_doctype": reverse_je.doctype,
            "payment_name": reverse_je.name,
            "amount": reverse_je.total_debit,
        }
        add_payment_entry(reverse_bank_tx_doc, voucher)
        ## Add Clearance Date
        frappe.db.set_value(
            "Journal Entry",
            reverse_je.name,
            "clearance_date",
            reverse_bank_tx_doc.date.strftime("%Y-%m-%d"),
        )

    # Finally Bounce Donation Receipt
    receipt_doc.db_set("workflow_state", "Bounced")
    receipt_doc.db_set("docstatus", 2)


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

    je = frappe.get_all(
        "Journal Entry",
        fields="name",
        filters={"donation_receipt": receipt_doc.name, "docstatus": 1},
    )

    if len(je) != 1:
        frappe.throw("There is no JE associated.")
    je = je[0]
    je_dict = frappe.get_doc("Journal Entry", je["name"]).as_dict()

    transaction_amount = je_dict["total_debit"]

    for a in je_dict["accounts"]:
        if a["debit"] == 0:
            a["debit"] = transaction_amount
            a["debit_in_account_currency"] = transaction_amount
            a["credit"] = 0
            a["credit_in_account_currency"] = 0
        elif a["credit"] == 0:
            a["credit"] = transaction_amount
            a["credit_in_account_currency"] = transaction_amount
            a["debit"] = 0
            a["debit_in_account_currency"] = 0

    del je_dict["clearance_date"]
    del je_dict["bank_statement_name"]
    del je_dict["name"]

    je_dict["posting_date"] = cash_return_date
    je_dict["user_remark"] = je_dict["user_remark"].replace(
        "BEING AMOUNT RECEIVED", "BEING CASH RETURNED"
    )

    reverse_je = frappe.get_doc(je_dict)
    reverse_je.submit()

    # Finally Cash Return Donation Receipt
    receipt_doc.db_set("workflow_state", "Cash Returned")
    receipt_doc.db_set("docstatus", 2)


##### CANCELLATION PROCEDURE #####
############# BEGIN ##############


# To cancel connected Journal Entry & detach Journal Entry from Bank Trasaction
@frappe.whitelist()
def receipt_cancel_operations(receipt):
    # Check for Permissions
    frappe.only_for("DCC Manager")
    #########################

    receipt_doc = frappe.get_doc("Donation Receipt", receipt)

    if receipt_doc.payment_method == CASH_PAYMENT_MODE:
        frappe.only_for("System Manager")

    je = frappe.db.get_list(
        "Journal Entry",
        filters={"donation_receipt": receipt, "docstatus": 1},
        pluck="name",
    )
    if len(je) > 1:
        frappe.throw(
            "There are multiple Journal Entries against this. This seems to be incoherent. Please contact Administrator."
        )
    elif len(je) == 1:
        je = je[0]

        # Cancel JE
        frappe.db.set_value("Journal Entry", je, "docstatus", 2)
        je_doc = frappe.get_doc("Journal Entry", je)
        je_doc.make_gl_entries(cancel=1)

        # Detach Bank Statement
        if je_doc.voucher_type != "Cash Entry":
            detach_bank_transaction(je)

    # Payment Gateway Unset
    if receipt_doc.payment_gateway_document:
        frappe.db.set_value(
            "Payment Gateway Transaction",
            receipt_doc.payment_gateway_document,
            {"receipt_created": 0, "donor": None, "seva_type": None},
        )
        pg_batch = frappe.db.get_value(
            "Payment Gateway Transaction", receipt_doc.payment_gateway_document, "batch"
        )

        refresh_pg_upload_batch(pg_batch)

    # Cancel Asset
    if receipt_doc.asset_item:
        assets = frappe.db.get_all(
            "Asset",
            filters={"custom_donation_receipt": receipt, "docstatus": 1},
            pluck="name",
        )
        if len(assets) > 0:
            asset = assets[0]
            asset_doc = frappe.get_doc("Asset", asset)
            asset_doc.cancel()

    # Finally Cancel Donation Receipt
    receipt_doc.docstatus = DocStatus.cancelled()
    receipt_doc.save(ignore_permissions=True)
    receipt_doc.db_set("workflow_state", "Cancelled")


def detach_bank_transaction(je):
    tx = frappe.get_all(
        "Bank Transaction",
        filters={"payment_document": "Journal Entry", "payment_entry": je},
    )
    # if len(tx) != 1:
    #     frappe.throw(
    #         "There is not a SINGLE Bank Transaction Entry. Either 0 or more than 1. Contact Administrator."
    #     )
    if len(tx) > 0:
        tx = tx[0]
        tx_doc = frappe.get_doc("Bank Transaction", tx)
        row = next(r for r in tx_doc.payment_entries if r.payment_entry == je)
        tx_doc.remove(row)
        tx_doc.save()
