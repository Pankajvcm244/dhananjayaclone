# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

from dhananjaya.dhananjaya.doctype.donation_receipt.constants import (
    CASH_PAYMENT_MODE,
    TDS_PAYMENT_MODE,
)
import frappe
from collections import defaultdict


def execute(filters=None):
    return DhananjayaDonationReceipt(filters).get_data()


class DhananjayaDonationReceipt(object):
    def __init__(self, filters):
        self.filters = frappe._dict(filters)
        self.columns = []
        self.conditions = ""
        self.set_columns()
        self.set_conditions()

    def set_conditions(self):
        conditions = ""
        conditions += f""" 
                        AND tdr.receipt_date
                            BETWEEN "{self.filters.from_date}" 
                                AND "{self.filters.to_date}" 
                        AND (gle.name IS NULL OR gle.posting_date
                            BETWEEN "{self.filters.from_date}" 
                                AND "{self.filters.to_date}"
                                )
                        """

        if self.filters.get("company"):
            conditions += f' AND tdr.company = "{self.filters.get("company")}"'

        if self.filters.get("preacher"):
            conditions += f' AND tdr.preacher = "{self.filters.get("preacher")}"'

        if self.filters.get("donor"):
            conditions += f' AND tdr.donor = "{self.filters.get("donor")}"'

        if self.filters.get("seva_type"):
            conditions += f' AND tdr.seva_type = "{self.filters.get("seva_type")}"'

        if self.filters.get("seva_subtype"):
            conditions += (
                f' AND tdr.seva_subtype = "{self.filters.get("seva_subtype")}"'
            )

        conditions += f""" AND (
                                ( gle.name IS NULL AND tdr.workflow_state = 'Realized') 
                                OR (gle.name IS NOT NULL and gle.account = tdr.donation_account)
                            )"""

        self.conditions = conditions

    def get_data(self):
        receipts = {}
        for i in frappe.db.sql(
            f"""
                        select tdr.*, 
                            COALESCE( SUM(gle.credit - gle.debit), tdr.amount) as total_donation,
                            CASE tdr.payment_method
                                WHEN '{CASH_PAYMENT_MODE}' THEN tdr.cash_account
                                WHEN '{TDS_PAYMENT_MODE}' THEN tdr.tds_account
                                ELSE tdr.bank_account
                            END as destination
                        from `tabDonation Receipt` tdr
                        left join `tabGL Entry` gle on gle.voucher_no = tdr.name
                        where 1 {self.conditions}
                        group by tdr.name
                        order by tdr.receipt_date
                        """,
            as_dict=1,
        ):
            i["total_received"] = i["total_donation"] - i["additional_charges"]
            receipts.setdefault(i["name"], i)

        donors = {}

        if len(receipts.keys()) > 0:
            for i in frappe.db.sql(
                f"""
                        select name as donor_id,
                        pan_no,
                        aadhar_no
                        from `tabDonor`
                        where name IN ({",".join([f"'{receipt['donor']}'" for receipt in receipts.values()])})
                        group by name
                        """,
                as_dict=1,
            ):
                donors.setdefault(i["donor_id"], i)
            for r in receipts:
                donor_id = receipts[r]["donor"]
                if donor_id:
                    receipts[r]["kyc"] = (
                        donors[donor_id]["pan_no"]
                        if donors[donor_id]["pan_no"]
                        else donors[donor_id]["aadhar_no"]
                    )

        if self.filters.get("group_by_seva_type"):
            seva_type_map = {}
            for r in receipts.values():
                if (r["seva_type"], r["donation_account"]) not in seva_type_map:
                    seva_type_map.setdefault(
                        (r["seva_type"], r["donation_account"]),
                        frappe._dict(
                            seva_type=r["seva_type"],
                            donation_account=r["donation_account"],
                            total_donation=r["total_donation"],
                        ),
                    )
                else:
                    seva_type_map[(r["seva_type"], r["donation_account"])][
                        "total_donation"
                    ] += r["total_donation"]
            data = list(seva_type_map.values())
            data.sort(key=lambda x: (x["seva_type"]))
        else:
            data = list(receipts.values())
            data.sort(key=lambda x: (x["company"], x["receipt_date"]), reverse=True)

        # columns, data = [], []
        return self.columns, data

    def set_columns(self):
        if self.filters.group_by_seva_type:
            self.columns = [
                {
                    "fieldname": "seva_type",
                    "label": "Seva Type",
                    "fieldtype": "Data",
                    "width": 250,
                },
                {
                    "fieldname": "donation_account",
                    "label": "Account",
                    "fieldtype": "Data",
                    "width": 250,
                },
                {
                    "fieldname": "total_donation",
                    "label": "Total Donation (Given Duration)",
                    "fieldtype": "Currency",
                    "width": 200,
                },
            ]
        else:
            self.columns = [
                {
                    "fieldname": "name",
                    "label": "ID",
                    "fieldtype": "Link",
                    "options": "Donation Receipt",
                    "width": 140,
                },
                {
                    "fieldname": "workflow_state",
                    "label": "State",
                    "fieldtype": "Data",
                    "width": 140,
                },
                {
                    "fieldname": "receipt_date",
                    "label": "Receipt Date",
                    "fieldtype": "Date",
                    "width": 120,
                },
                {
                    "fieldname": "company_abbreviation",
                    "label": "Company",
                    "fieldtype": "Data",
                    "width": 100,
                },
                {
                    "fieldname": "donor",
                    "label": "Donor",
                    "fieldtype": "Link",
                    "options": "Donor",
                    "width": 140,
                },
                {
                    "fieldname": "full_name",
                    "label": "Full Name",
                    "fieldtype": "Data",
                    "width": 200,
                },
                {
                    "fieldname": "preacher",
                    "label": "Preacher",
                    "fieldtype": "Data",
                    "width": 100,
                },
                {
                    "fieldname": "total_donation",
                    "label": "Total Donation (Given Duration)",
                    "fieldtype": "Currency",
                    "width": 200,
                },
                {
                    "fieldname": "additional_charges",
                    "label": "Charges",
                    "fieldtype": "Currency",
                    "width": 200,
                },
                {
                    "fieldname": "total_received",
                    "label": "Total Received",
                    "fieldtype": "Currency",
                    "width": 200,
                },
                {
                    "fieldname": "payment_method",
                    "label": "Payment Method",
                    "fieldtype": "Data",
                    "width": 120,
                },
                {
                    "fieldname": "destination",
                    "label": "Destination",
                    "fieldtype": "Data",
                    "width": 120,
                },
                {
                    "fieldname": "seva_type",
                    "label": "Seva Type",
                    "fieldtype": "Data",
                    "width": 200,
                },
                {
                    "fieldname": "contact",
                    "label": "Donor Contact",
                    "fieldtype": "Data",
                    "width": 200,
                },
                {
                    "fieldname": "address",
                    "label": "Donor Address",
                    "fieldtype": "Data",
                    "width": 500,
                },
                {
                    "fieldname": "kyc",
                    "label": "KYC",
                    "fieldtype": "Data",
                    "width": 200,
                },
                {
                    "fieldname": "atg_required",
                    "label": "80G",
                    "fieldtype": "Check",
                    "width": 100,
                },
                {
                    "fieldname": "is_ecs",
                    "label": "ECS",
                    "fieldtype": "Check",
                    "width": 100,
                },
                {
                    "fieldname": "is_csr",
                    "label": "CSR",
                    "fieldtype": "Check",
                    "width": 100,
                },
            ]
