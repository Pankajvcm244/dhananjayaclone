from dhananjaya.dhananjaya.extra_utils.sheets import get_data_from_google_sheets
import frappe


@frappe.whitelist(methods=["POST"])
def process():
    operations_doc = frappe.get_single("DJ Bank Operations")
    if not operations_doc.vendor_payment_gs_link:
        frappe.throw("There is no link avaialble.")
    rows = get_data_from_google_sheets(operations_doc.vendor_payment_gs_link)
    headers = rows[0]
    if (
        not [
            "Bank Transaction",
            "Account",
            "Party Type",
            "Party",
            "Reference Type",
            "Reference Name",
            "User Remark",
        ]
        == headers
    ):
        frappe.throw("Google Sheets File is Corrupt. Headers are not matching.")

    for raw in rows[1:]:
        create_journal_entry(raw)


def create_journal_entry(raw):
    statement = raw[0]
    if not statement:
        return
    account = raw[1]
    party_type = raw[2]
    party = raw[3]
    reference_type = raw[4]
    reference_name = raw[5]
    user_remarks = raw[6]

    bank_transaction = frappe.get_doc("Bank Transaction", statement)
    company_account = frappe.get_value(
        "Bank Account", bank_transaction.bank_account, "account"
    )
    company = frappe.get_value("Account", company_account, "company")

    COST_CENTER = frappe.db.get_value(
        "Company", bank_transaction.company, "cost_center"
    )
    accounts = []
    accounts.append(
        {
            "account": account,
            "party_type": party_type,
            "party": party,
            "credit_in_account_currency": bank_transaction.deposit,
            "debit_in_account_currency": bank_transaction.withdrawal,
            "cost_center": COST_CENTER,
            "reference_type": reference_type,
            "reference_name": reference_name,
        }
    )
    accounts.append(
        {
            "account": company_account,
            "bank_account": bank_transaction.bank_account,
            "credit_in_account_currency": bank_transaction.withdrawal,
            "debit_in_account_currency": bank_transaction.deposit,
            "cost_center": COST_CENTER,
        }
    )

    journal_entry_dict = {
        "voucher_type": "Bank Entry",
        "company": company,
        "bank_statement_name": bank_transaction.name,
        "posting_date": bank_transaction.date,
        "cheque_date": bank_transaction.date,
        "cheque_no": bank_transaction.description,
        "user_remark": user_remarks,
    }
    journal_entry = frappe.new_doc("Journal Entry")
    journal_entry.update(journal_entry_dict)
    journal_entry.set("accounts", accounts)
    journal_entry.submit()
