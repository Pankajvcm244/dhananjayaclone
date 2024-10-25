from dhananjaya.dhananjaya.utils import get_company_defaults
from erpnext.accounts.general_ledger import make_gl_entries
import frappe


# def execute():
#     set_cost_center_in_exisintg_receipt()
#     remove_old_jes()


# def set_precher_in_puja():
#     for pp in frappe.get_all(
#         "Patron Privilege Puja",
#         filters={"preacher": ("is", "not set")},
#         fields=["name", "patron"],
#     ):
#         preacher = frappe.get_value("Patron", pp["patron"], "llp_preacher")
#         frappe.set_value("Patron Privilege Puja", pp["name"], "preacher", preacher)


def correct_cheques():
    for c in frappe.db.sql(
        """
        SELECT 
            tdr.name,
            tdr.receipt_date, 
            tdr.cheque_date, 
            tdr.donation_account,
            COUNT(tgl.name) as gls,
            GROUP_CONCAT(tgl.name SEPARATOR ',') as gl_data
        FROM `tabDonation Receipt` tdr
        JOIN `tabGL Entry` tgl
            ON tgl.voucher_type = 'Donation Receipt' AND tgl.voucher_no = tdr.name
        WHERE tdr.payment_method = 'Cheque' AND tdr.workflow_state = 'Realized'
            AND tdr.cheque_date != tdr.receipt_date
        GROUP BY tdr.name
        HAVING gls > 2
        """,
        as_dict=1,
    ):
        print(
            f"Processing Receipt : {c.name} | Receipt Date : {c.receipt_date} | Cheque Date : {c.cheque_date}"
        )
        donation_gl = None
        temp_gl = None
        for gl in frappe.get_all(
            "GL Entry",
            filters={"voucher_type": "Donation Receipt", "voucher_no": c.name},
            fields=["name", "account", "posting_date", "debit", "credit"],
        ):
            if gl.account == c.donation_account and gl.credit > 0:
                donation_gl = gl
            elif "Temporary Cheque" in gl.account and gl.debit > 0:
                temp_gl = gl

        if donation_gl and temp_gl:
            print("Modifying")
            frappe.db.set_value(
                "GL Entry", donation_gl.name, "posting_date", c.cheque_date
            )
            frappe.db.set_value("GL Entry", temp_gl.name, "posting_date", c.cheque_date)
            frappe.db.set_value(
                "Donation Receipt", c.name, "receipt_date", c.cheque_date
            )
        else:
            print("Skipping")


def set_cost_center_in_exisintg_receipt():
    for c in frappe.get_all("Company", fields=["name", "abbr"]):
        cost_center = "Main - " + c.abbr
        frappe.db.sql(
            f"""
            UPDATE `tabDonation Receipt`
            SET cost_center = '{cost_center}'
            WHERE 
                company = '{c.name}' 
                AND cost_center IS NULL
        """
        )


def remove_old_jes():
    all_docs = frappe.db.sql(
        """
        SELECT 
            tdr.name as donation_receipt,
            tje.name as journal_entry,
            tgl.name as gl_entry,
            tdr.company as receipt_company,
            tje.company as je_company
        FROM `tabDonation Receipt` tdr
        JOIN `tabJournal Entry` tje
            ON tje.donation_receipt = tdr.name
        LEFT JOIN `tabGL Entry` tgl
            ON tgl.voucher_type = 'Journal Entry' AND tgl.voucher_no = tje.name
        """,
        as_dict=1,
    )

    all_jes = list(set([a["journal_entry"] for a in all_docs]))

    je_batches = [all_jes[i : i + 1000] for i in range(0, len(all_jes), 1000)]

    for bi, b in enumerate(je_batches):
        for index, a in enumerate(b):
            print(f"Processing {bi}:{index+1}")
            frappe.delete_doc(
                "Journal Entry", a, True, ignore_permissions=True, ignore_on_trash=True
            )

        frappe.db.commit()

    all_gls = list(set([a["gl_entry"] for a in all_docs if a["gl_entry"]]))
    for a in all_gls:
        frappe.delete_doc("GL Entry", a)

        # for a in all_inaccurate_jes:
        #     frappe.db.set_value("Journal Entry", a, "donation_receipt", None)


# def execute():
#     readjust_gl_and_bank_txs()
#     receipt_date_update()
#     create_temporary_ledgers()
#     update_statuses()


# def readjust_gl_and_bank_txs():
#     ## Refurbish GL Entries
#     print("Cleaning GL Entries")
#     for e in frappe.db.sql(
#         """
#         SELECT tdr.name as donation_receipt,tgl.name as gl_entry
#         FROM `tabDonation Receipt` tdr
#         JOIN `tabJournal Entry` tje
#             ON tje.donation_receipt = tdr.name
#         JOIN `tabGL Entry` tgl
#             ON tgl.voucher_type = 'Journal Entry' AND tgl.voucher_no = tje.name
#         """,
#         as_dict=1,
#     ):
#         frappe.db.set_value(
#             "GL Entry",
#             e["gl_entry"],
#             {"voucher_type": "Donation Receipt", "voucher_no": e["donation_receipt"]},
#         )
#     print("Cleaning Bank Transaction Entries")
#     ## Refurbish Bank Transaction Entries
#     for e in frappe.db.sql(
#         """
#         SELECT tdr.name as donation_receipt,tbtp.name as bt_entry
#         FROM `tabDonation Receipt` tdr
#         JOIN `tabJournal Entry` tje
#             ON tje.donation_receipt = tdr.name
#         JOIN `tabBank Transaction Payments` tbtp
#             ON tbtp.payment_document = 'Journal Entry' AND tbtp.payment_entry = tje.name
#         """,
#         as_dict=1,
#     ):
#         frappe.db.set_value(
#             "Bank Transaction Payments",
#             e["bt_entry"],
#             {
#                 "payment_document": "Donation Receipt",
#                 "payment_entry": e["donation_receipt"],
#             },
#         )


# def receipt_date_update():
#     ## Cheque
#     # frappe.db.sql(
#     #     """
#     #     UPDATE `tabDonation Receipt`
#     #     SET receipt_date = cheque_date
#     #     WHERE docstatus = 1
#     #         AND payment_method = 'Cheque'
#     #         AND cheque_date IS NOT NULL
#     #         """
#     # )

#     ## Update Receipt Date
#     frappe.db.sql(
#         """
#         UPDATE `tabDonation Receipt`
#         SET old_receipt_date = receipt_date
#         WHERE docstatus = 1
#             AND realization_date IS NOT NULL
#             """
#     )
#     frappe.db.sql(
#         """
#         UPDATE `tabDonation Receipt`
#         SET receipt_date = realization_date
#         WHERE docstatus = 1
#             AND realization_date IS NOT NULL
#             """
#     )


# def update_statuses():
#     print("Changing Statuses")
#     ## Change status of Cash Donations to Realized
#     frappe.db.sql(
#         """
#         UPDATE `tabDonation Receipt`
#         SET workflow_state = 'Realized'
#         WHERE workflow_state = 'Received by Cashier'
#             """
#     )

#     ## Change docstatus of Bounced/Cash Returned Donations
#     frappe.db.sql(
#         """
#         UPDATE `tabDonation Receipt`
#         SET docstatus = 1
#         WHERE workflow_state = 'Bounced'
#             """
#     )
#     frappe.db.sql(
#         """
#         UPDATE `tabDonation Receipt`
#         SET docstatus = 1
#         WHERE workflow_state = 'Cash Returned'
#             """
#     )


# def create_temporary_ledgers():
#     def create_account(company, acc_str):
#         abbr = frappe.db.get_value("Company", company, "abbr")
#         parent_account = "Temporary Accounts - " + abbr
#         if not frappe.db.exists("Account", parent_account):
#             frappe.get_doc(
#                 {
#                     "doctype": "Account",
#                     "account_name": "Temporary Accounts",
#                     "is_group": 1,
#                     "company": company,
#                     "parent_account": "Application of Funds (Assets) - " + abbr,
#                 }
#             ).insert(ignore_permissions=True)
#         if not frappe.db.exists("Account", acc_str + " - " + abbr):
#             doc = frappe.get_doc(
#                 {
#                     "doctype": "Account",
#                     "account_name": acc_str,
#                     "account_type": "Temporary",
#                     "company": company,
#                     "parent_account": "Temporary Accounts - " + abbr,
#                 }
#             )
#             doc.insert(ignore_permissions=True)
#             return doc.name
#         else:
#             return frappe.db.get_value("Account", acc_str + " - " + abbr, "name")

#     settings = frappe.get_single("Dhananjaya Settings")

#     cheque_str = "Temporary Cheque"
#     cash_str = "Temporary Cash"
#     gateway_str = "Temporary Gateway"

#     for cd in settings.company_details:
#         if not cd.temporary_cash_account:
#             cd.temporary_cash_account = create_account(cd.company, cash_str)
#         if not cd.temporary_cheque_account:
#             cd.temporary_cheque_account = create_account(cd.company, cheque_str)
#         if not cd.temporary_gateway_account:
#             cd.temporary_gateway_account = create_account(cd.company, gateway_str)

#     settings.save(ignore_permissions=True)


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
