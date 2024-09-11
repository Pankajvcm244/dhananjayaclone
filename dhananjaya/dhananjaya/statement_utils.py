import frappe
from frappe.utils.data import today


@frappe.whitelist()
def get_donation_receipt_from_statement(statement):
    bank_transaction = frappe.get_doc("Bank Transaction", statement)
    payment_method = None

    if "NEFT" in bank_transaction.description:
        payment_method = "NEFT/IMPS"
    elif "UPI" in bank_transaction.description:
        payment_method = "UPI"

    dr_dict = {
        "company": bank_transaction.company,
        "receipt_date": today(),
        "payment_method": payment_method,
        "amount": bank_transaction.unallocated_amount,
        "bank_account": bank_transaction.bank_account,
        "bank_transaction": bank_transaction.name,
    }

    donation_entry = frappe.new_doc("Donation Receipt")
    donation_entry.update(dr_dict)
    return donation_entry
