# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from collections import defaultdict


def execute(filters=None):
    conditions = get_conditions(filters)
    receipts = {}
    for i in frappe.db.sql(
        f"""
					select *
					from `tabDonation Receipt` tdr
					where docstatus = 1 {conditions}
					order by receipt_date
					""",
        as_dict=1,
    ):
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

    # data = list(receipts.values())

    # data = receipts
    columns = get_columns(filters)

    if filters.get("group_by_seva_type"):
        seva_type_map = {}
        for r in receipts.values():
            if (r["seva_type"], r["donation_account"]) not in seva_type_map:
                seva_type_map.setdefault(
                    (r["seva_type"], r["donation_account"]),
                    frappe._dict(
                        seva_type=r["seva_type"],
                        donation_account=r["donation_account"],
                        amount=r["amount"],
                    ),
                )
            else:
                seva_type_map[(r["seva_type"], r["donation_account"])]["amount"] += r[
                    "amount"
                ]
        data = list(seva_type_map.values())
        data.sort(key=lambda x: (x["seva_type"]))
    else:
        data = list(receipts.values())
        data.sort(key=lambda x: (x["company"], x["receipt_date"]), reverse=True)

    # columns, data = [], []
    return columns, data


def get_conditions(filters):
    conditions = ""
    if filters.get("based_on") == "realization_date":
        rd_condition = f""" 
                tdr.realization_date BETWEEN "{filters.get("from_date")}" AND "{filters.get("to_date")}"
                """
        if filters.get("include_non_realized_based_on_receipt_date"):
            rd_condition += f"""
                            OR (
                                tdr.realization_date IS NULL 
                                AND 
                                    tdr.receipt_date
                                    BETWEEN 
                                    "{filters.get("from_date")}" 
                                    AND "{filters.get("to_date")}"
                                )
                                """
        conditions += f" AND ({rd_condition})"
    else:
        conditions += f' AND tdr.{filters.get("based_on")} BETWEEN "{filters.get("from_date")}" AND "{filters.get("to_date")}"'

    if filters.get("company"):
        conditions += f' AND tdr.company = "{filters.get("company")}"'

    if filters.get("preacher"):
        conditions += f' AND tdr.preacher = "{filters.get("preacher")}"'

    if filters.get("donor"):
        conditions += f' AND tdr.donor = "{filters.get("donor")}"'

    if filters.get("seva_type"):
        conditions += f' AND tdr.seva_type = "{filters.get("seva_type")}"'

    if filters.get("seva_subtype"):
        conditions += f' AND tdr.seva_subtype = "{filters.get("seva_subtype")}"'

    return conditions


def get_columns(filters):
    if filters.get("group_by_seva_type"):
        columns = [
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
                "fieldname": "amount",
                "label": "Amount",
                "fieldtype": "Currency",
                "width": 200,
            },
        ]
    else:
        columns = [
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
                "fieldname": "realization_date",
                "label": "Realization Date",
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
                "fieldname": "amount",
                "label": "Amount",
                "fieldtype": "Currency",
                "width": 120,
            },
            {
                "fieldname": "payment_method",
                "label": "Payment Method",
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
    return columns
