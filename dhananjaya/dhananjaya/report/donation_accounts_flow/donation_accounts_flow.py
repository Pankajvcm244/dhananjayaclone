# Copyright (c) 2024, Narahari Dasa and contributors
# For license information, please see license.txt

import calendar
from datetime import datetime
from dhananjaya.dhananjaya.report import donation_accounts_flow
import frappe
from frappe import _
from frappe.utils.data import add_to_date, date_diff


def test():
    DonationAccountsFlow(
        {
            "company": "Hare Krishna Movement Jaipur",
            "from_date": "2024-04-01",
            "to_date": "2024-06-30",
            "accounts": ["HKCC Building Construction - HKMJ"],
        }
    ).get_data()


def execute(filters=None):
    return DonationAccountsFlow(filters).get_data()


class DonationAccountsFlow(object):
    def __init__(self, filters):
        self.filters = frappe._dict(filters)
        self.columns = []
        self.months = []
        self.data = frappe._dict()
        self.validate_filters()
        self.load_data()

    def load_data(self):
        self.get_month_year_dates_range()
        self.set_columns()
        self.map_donation_to_account()

    def get_data(self):
        # print(self.data)
        final_data = []
        for d in self.data.values():
            total_row = {"account": "Total", "total": 0}
            total_row.update({m.key: 0 for m in self.months})
            print(total_row)
            for index, fund_row in enumerate(d.fund_accounts.values()):
                final_data_row = frappe._dict()
                if index == 0:
                    final_data_row.donation_account = d.donation_account
                else:
                    final_data_row.donation_account = ""
                final_data_row.update(fund_row)
                final_data.append(final_data_row)
                for m in self.months:
                    total_row[m.key] += fund_row.get(m.key, 0)
                    total_row["total"] += fund_row.get(m.key, 0)
            final_data.append(total_row)

        return self.columns, final_data

    def map_donation_to_account(self):
        for account in self.filters.accounts:
            if account not in self.data:
                self.data.setdefault(
                    account,
                    frappe._dict(
                        donation_account=account, fund_accounts=frappe._dict()
                    ),
                )
            for month in self.months:
                for fa in self.get_donation_account_data(account, month):
                    if fa.account not in self.data[account].fund_accounts:
                        self.data[account].fund_accounts.setdefault(
                            fa.account, frappe._dict(account=fa.account, total=0)
                        )
                    self.data[account].fund_accounts[fa.account][
                        month.key
                    ] = fa.total_debit
                    self.data[account].fund_accounts[fa.account].total += fa.total_debit

    def get_donation_account_data(self, donation_account, month):
        vouchers = frappe.get_all(
            "GL Entry",
            filters={
                "account": donation_account,
                "posting_date": ["between", [month.start_date, month.end_date]],
            },
            pluck="voucher_no",
        )
        vouchers = list(set(vouchers))
        vouchers_str = ",".join([f"'{v}'" for v in vouchers])
        return frappe.db.sql(
            f"""
            SELECT account,
                SUM(debit-credit) as total_debit
            FROM `tabGL Entry`
            WHERE voucher_no IN ({vouchers_str})
                AND is_cancelled = 0
            GROUP BY account
                """,
            as_dict=1,
        )
        # for v in vouchers:

    def validate_filters(self):
        if not self.filters.get("from_date") and self.filters.get("to_date"):
            frappe.throw(_("From and To Dates are required."))
        elif date_diff(self.filters.to_date, self.filters.from_date) < 0:
            frappe.throw(_("To Date cannot be before From Date."))

    def get_month_year_dates_range(self):
        start = datetime.strptime(self.filters.get("from_date"), "%Y-%m-%d")
        end = datetime.strptime(self.filters.get("to_date"), "%Y-%m-%d")

        current = start
        date_ranges = []

        while current <= end:
            # Start date of the current month
            month_start = current.strftime("%Y-%m-%d")
            # Total days in the month
            days = calendar.monthrange(current.year, current.month)[1]
            last_day = datetime(year=current.year, month=current.month, day=days)
            month_end = min(end, last_day).strftime("%Y-%m-%d")
            unique_key = current.strftime("%Y%m")

            # Format the output
            formatted_range = frappe._dict(
                key=unique_key,
                label=current.strftime("%B - %y"),
                start_date=month_start,
                end_date=month_end,
            )
            date_ranges.append(formatted_range)

            current = add_to_date(last_day, days=1)

        self.months = date_ranges

    def set_columns(self):
        columns = [
            {
                "fieldname": "donation_account",
                "label": "Donation Account",
                "fieldtype": "Data",
                "width": 200,
            },
            {
                "fieldname": "account",
                "label": "Fund Account",
                "fieldtype": "Data",
                "width": 300,
            },
        ]
        for month in self.months:
            columns.append(
                {
                    "fieldname": month.key,
                    "label": month.label,
                    "fieldtype": "Currency",
                    "width": 200,
                },
            )
        columns.append(
            {
                "fieldname": "total",
                "label": "Total",
                "fieldtype": "Currency",
                "width": 200,
            },
        )

        self.columns = columns
