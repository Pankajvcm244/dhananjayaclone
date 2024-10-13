from dhananjaya.dhananjaya.utils import get_company_defaults
from erpnext.accounts.general_ledger import make_gl_entries
import frappe


def execute():
    readjust_gl_and_bank_txs()
    receipt_date_update()
    create_temporary_ledgers()
    update_statuses()


def readjust_gl_and_bank_txs():
    ## Refurbish GL Entries
    print("Cleaning GL Entries")
    for e in frappe.db.sql(
        """
        SELECT tdr.name as donation_receipt,tgl.name as gl_entry
        FROM `tabDonation Receipt` tdr
        JOIN `tabJournal Entry` tje
            ON tje.donation_receipt = tdr.name
        JOIN `tabGL Entry` tgl
            ON tgl.voucher_type = 'Journal Entry' AND tgl.voucher_no = tje.name
        """,
        as_dict=1,
    ):
        frappe.db.set_value(
            "GL Entry",
            e["gl_entry"],
            {"voucher_type": "Donation Receipt", "voucher_no": e["donation_receipt"]},
        )
    print("Cleaning Bank Transaction Entries")
    ## Refurbish Bank Transaction Entries
    for e in frappe.db.sql(
        """
        SELECT tdr.name as donation_receipt,tbtp.name as bt_entry
        FROM `tabDonation Receipt` tdr
        JOIN `tabJournal Entry` tje
            ON tje.donation_receipt = tdr.name
        JOIN `tabBank Transaction Payments` tbtp
            ON tbtp.payment_document = 'Journal Entry' AND tbtp.payment_entry = tje.name
        """,
        as_dict=1,
    ):
        frappe.db.set_value(
            "Bank Transaction Payments",
            e["bt_entry"],
            {
                "payment_document": "Donation Receipt",
                "payment_entry": e["donation_receipt"],
            },
        )


def receipt_date_update():
    ## Cheque
    # frappe.db.sql(
    #     """
    #     UPDATE `tabDonation Receipt`
    #     SET receipt_date = cheque_date
    #     WHERE docstatus = 1
    #         AND payment_method = 'Cheque'
    #         AND cheque_date IS NOT NULL
    #         """
    # )

    ## Update Receipt Date
    frappe.db.sql(
        """
        UPDATE `tabDonation Receipt`
        SET old_receipt_date = receipt_date
        WHERE docstatus = 1
            AND realization_date IS NOT NULL
            """
    )
    frappe.db.sql(
        """
        UPDATE `tabDonation Receipt`
        SET receipt_date = realization_date
        WHERE docstatus = 1
            AND realization_date IS NOT NULL
            """
    )


def update_statuses():
    print("Changing Statuses")
    ## Change status of Cash Donations to Realized
    frappe.db.sql(
        """
        UPDATE `tabDonation Receipt`
        SET workflow_state = 'Realized'
        WHERE workflow_state = 'Received by Cashier'       
            """
    )

    ## Change docstatus of Bounced/Cash Returned Donations
    frappe.db.sql(
        """
        UPDATE `tabDonation Receipt`
        SET docstatus = 1
        WHERE workflow_state = 'Bounced'       
            """
    )
    frappe.db.sql(
        """
        UPDATE `tabDonation Receipt`
        SET docstatus = 1
        WHERE workflow_state = 'Cash Returned'       
            """
    )


def create_temporary_ledgers():
    def create_account(company, acc_str):
        abbr = frappe.db.get_value("Company", company, "abbr")
        if not frappe.db.exists("Account", acc_str + " - " + abbr):
            doc = frappe.get_doc(
                {
                    "doctype": "Account",
                    "account_name": acc_str,
                    "account_type": "Temporary",
                    "company": company,
                    "parent_account": "Temporary Accounts - " + abbr,
                }
            )
            doc.insert(ignore_permissions=True)
            return doc.name
        else:
            return frappe.db.get_value("Account", acc_str + " - " + abbr, "name")

    settings = frappe.get_single("Dhananjaya Settings")

    cheque_str = "Temporary Cheque"
    cash_str = "Temporary Cash"
    gateway_str = "Temporary Gateway"

    for cd in settings.company_details:
        if not cd.temporary_cash_account:
            cd.temporary_cash_account = create_account(cd.company, cash_str)
        if not cd.temporary_cheque_account:
            cd.temporary_cheque_account = create_account(cd.company, cheque_str)
        if not cd.temporary_gateway_account:
            cd.temporary_gateway_account = create_account(cd.company, gateway_str)

    settings.save(ignore_permissions=True)


# def adjust_cheque_gl_entries():
#     for d in frappe.db.sql(
#         """
#     SELECT name,company,cheque_date, donation_account, bank_transaction,amount
#     FROM  `tabDonation Receipt`
#     WHERE docstatus = 1
#         AND workflow_state = 'Realized'
#         AND payment_method = 'Cheque'
#     """,
#         as_dict=1,
#     ):
#         if d.bank_transaction:
#             company_detail = get_company_defaults(d.company)
#             # bank_tx_date = frappe.db.get_value(
#             #     "Bank Transaction", d.bank_transaction, "date"
#             # )
#             gl_entries = frappe.get_all(
#                 "GL Entry",
#                 filters={"voucher_type": "Donation Receipt", "voucher_no": d.name},
#                 fields=["name", "posting_date", "account", "credit", "debit"],
#             )
#             posting_date = gl_entries[0].posting_date

#             for gl in gl_entries:
#                 if gl.credit > 0:
#                     frappe.db.set_value(
#                         "GL Entry", gl.name, "posting_date", d.cheque_date
#                     )

#             temp_gl_base_entries = [
#                 frappe._dict(
#                     posting_date=d.cheque_date,
#                     account=company_detail.temporary_cheque_account,
#                     debit=d.amount,
#                 ),
#                 frappe._dict(
#                     posting_date=posting_date,
#                     account=company_detail.temporary_cheque_account,
#                     credit=d.amount,
#                 ),
#             ]
#             receipt_doc = frappe.get_doc("Donation Receipt", d.name)
#             gl_entries = []
#             for gb in temp_gl_base_entries:
#                 gl_entries.append(
#                     receipt_doc.get_gl_dict(
#                         {
#                             **gb,
#                             **{
#                                 "cost_center": receipt_doc.cost_center,
#                                 "project": receipt_doc.project,
#                             },
#                         },
#                         item=receipt_doc,
#                     )
#                 )
#             make_gl_entries(gl_entries, merge_entries=False)
