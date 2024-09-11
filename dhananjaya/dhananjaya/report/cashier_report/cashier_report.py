# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import json
import frappe


def execute(filters=None):
    data = []
    cash_accounts = frappe.get_all(
        "Account",
        pluck="name",
        filters={
            "disabled": 0,
            "is_group": 0,
            "account_type": "Cash",
            "company": filters.get("company"),
        },
    )
    cash_accounts_str = ", ".join([f"'{a}'" for a in cash_accounts])
    cash_accounts_opening = get_opening_balances(
        cash_accounts, filters.get("from_date")
    )
    cash_accounts_closing = get_closing_balances(cash_accounts, filters.get("to_date"))
    columns = get_expense_colums(cash_accounts)
    entries = {"opening": {"voucher_entry": "Opening", **cash_accounts_opening}}

    for j in frappe.db.sql(
        f"""
				SELECT 
					DATE_FORMAT(tgl.creation, "%D %b, %Y") as entry_date,
                    DATE_FORMAT(tgl.creation, "%I:%i %p") as entry_time,
                    tgl.voucher_no as voucher_entry,
					tgl.posting_date, tgl.against, tgl.account as cash_account, tgl.debit, tgl.credit,
					tgl.owner as cashier,
					tje.donation_receipt,
                    tje.user_remark as remarks
				FROM `tabGL Entry` tgl
                LEFT JOIN `tabJournal Entry` tje ON tje.name = tgl.voucher_no
				WHERE tgl.company = '{filters.get('company')}'
				AND tgl.account IN ({cash_accounts_str})
				AND tgl.posting_date BETWEEN '{filters.get('from_date')}' AND '{filters.get('to_date')}'
                AND tgl.is_cancelled = 0
				ORDER BY tgl.creation
						""",
        as_dict=1,
    ):
        if j.voucher_entry not in entries:
            entries[j.voucher_entry] = j
            for c in cash_accounts:
                entries[j.voucher_entry][c] = 0
        entries[j.voucher_entry][j.cash_account] += j.debit - j.credit

    entries.update({"closing": {"voucher_entry": "Closing", **cash_accounts_closing}})
    data = list(entries.values())

    return columns, data


def get_opening_balances(accounts, start_date):
    accounts_map = {}
    for a in frappe.db.sql(
        f"""
            SELECT account, SUM(debit-credit) as balance
            FROM `tabGL Entry`
            WHERE account IN ({",".join([f"'{a}'" for a in accounts])})
            AND is_cancelled = 0
            AND posting_date < '{start_date}'
            GROUP BY account
            """,
        as_dict=1,
    ):
        accounts_map.setdefault(a.account, a.balance)
    return accounts_map


def get_closing_balances(accounts, end_date):
    accounts_map = {}
    for a in frappe.db.sql(
        f"""
            SELECT account, SUM(debit-credit) as balance
            FROM `tabGL Entry`
            WHERE account IN ({",".join([f"'{a}'" for a in accounts])})
            AND is_cancelled = 0
            AND posting_date <= '{end_date}'
            GROUP BY account
            """,
        as_dict=1,
    ):
        accounts_map.setdefault(a.account, a.balance)
    return accounts_map


def get_expense_colums(cash_accounts):
    columns = [
        {
            "fieldname": "entry_date",
            "fieldtype": "Data",
            "label": "Creation Date",
            "width": 130,
        },
        {
            "fieldname": "entry_time",
            "fieldtype": "Data",
            "label": "Time",
            "width": 100,
        },
        {
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "label": "Posting Date",
            "width": 120,
        },
        {
            "fieldname": "voucher_entry",
            "fieldtype": "Data",
            "label": "Voucher Entry",
            "width": 200,
        },
    ]
    columns.extend(
        [
            {
                "fieldname": f"{account}",
                "fieldtype": "Currency",
                "label": f"{account}",
                "options": "Currency",
                "width": 150,
            }
            for account in cash_accounts
        ]
    )
    columns.extend(
        [
            {
                "fieldname": "donation_receipt",
                "fieldtype": "Link",
                "options": "Donation Receipt",
                "label": "Donation Receipt",
                "width": 200,
            },
            {
                "fieldname": "against",
                "fieldtype": "Link",
                "options": "Account",
                "label": "Against Head",
                "width": 300,
            },
            {
                "fieldname": "cashier",
                "fieldtype": "Data",
                "label": "Cashier",
                "width": 200,
            },
            {
                "fieldname": "remarks",
                "fieldtype": "Data",
                "label": "Remarks",
                "width": 500,
            },
        ]
    )
    return columns
