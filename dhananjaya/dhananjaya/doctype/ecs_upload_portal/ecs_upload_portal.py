# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import datetime
import json
from dhananjaya.dhananjaya.extra_utils.sheets import get_data_from_google_sheets
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.csvutils import get_csv_content_from_google_sheets, read_csv_content

ECS_PAYMENT_GATWEWAY_MODE = "NEFT/IMPS"


class ECSUploadPortal(Document):
    pass


def get_data_in_dict():
    ecs_portal = frappe.get_single("ECS Upload Portal")
    rows = get_data_from_google_sheets(ecs_portal.google_sheets_url)
    headers = rows[0]
    # return headers
    if (
        not [
            "Unique Reference Number",
            "Transaction ID",
            "Presentment Mode",
            "Customer Name",
            "Amount",
            "Date",
            "Status",
            "Reason Code",
            "Reason description",
        ]
        == headers
    ):
        frappe.throw("NACH Description File is Corrupt. Headers are not matching.")
    data = []
    for row in rows[1:]:
        data.append(
            {
                "Unique Reference Number": row[0],
                "Transaction ID": row[1],
                "Customer Name": row[3],
                "Amount": row[4],
                "Date": row[5],
                "Reason Code": row[7],
                "Reason description": row[8],
            }
        )
    return data


@frappe.whitelist()
def fetch_data():
    return json.dumps(get_data_in_dict())


######## ECS DATA PROCESS ########
############ BEGIN ###############


# Process all gateway payments received in a Batch.
@frappe.whitelist()
def process_ecs_data():
    ecs_portal = frappe.get_single("ECS Upload Portal")
    bank_tx_doc = frappe.get_doc("Bank Transaction", ecs_portal.bank_transaction)
    if not (ecs_portal.final_amount == bank_tx_doc.unallocated_amount):
        frappe.throw("This ECS Data processing is not eligible due to amount mismatch.")

    donor_data = {}
    for i in frappe.db.sql(
        """
					select ecs_id,name,ecs_default_seva_type,ecs_default_patron
					from `tabDonor`
					where ecs_id is not null
					""",
        as_dict=1,
    ):
        donor_data.setdefault(i["ecs_id"], i)

    ecs_data = {}
    gs_data = get_data_in_dict()
    for d in gs_data:
        ecs_data.setdefault(d["Unique Reference Number"], d)
        if d["Unique Reference Number"] not in donor_data:
            frappe.throw(
                f" Unique Reference Number <b>{d['Unique Reference Number']}</b> is not available in Donor Data."
            )
        else:
            this_donor = donor_data[d["Unique Reference Number"]]

            extra_data = frappe._dict(donor=this_donor["name"])

            if this_donor["ecs_default_seva_type"]:
                extra_data.setdefault("seva_type", this_donor["ecs_default_seva_type"])
                donor_ecs_company = frappe.get_value("Seva Type", extra_data["seva_type"], "company")
                if donor_ecs_company != bank_tx_doc.company:
                    frappe.throw(
                        f"Donor ID : {this_donor['name']} has a seva type which is not of the same company mentioned in ECS Upload Portal"
                    )
            else:
                extra_data.setdefault("seva_type", ecs_portal.seva_type)

            if this_donor["ecs_default_patron"]:
                extra_data.setdefault("patron", this_donor["ecs_default_patron"])

            ecs_data[d["Unique Reference Number"]].update(extra_data)

    for ecs_id, ecs in ecs_data.items():
        dr = {
            "doctype": "Donation Receipt",
            "company": bank_tx_doc.company,
            "is_ecs": 1,
            "ecs_transaction_id": ecs["Transaction ID"],
            # States as per Donor
            "docstatus": 0,
            "workflow_state": "Draft",
            # Rest of Data
            "donor": ecs["donor"],
            "seva_type": ecs["seva_type"],
            "receipt_date": datetime.datetime.strptime(ecs["Date"], "%d-%m-%Y %H:%M:%S").strftime("%Y-%m-%d"),
            "payment_method": ECS_PAYMENT_GATWEWAY_MODE,
            "amount": float(ecs["Amount"]),
            "bank_account": bank_tx_doc.bank_account,
            "bank_transaction": bank_tx_doc.name,
        }
        dr_doc = frappe.get_doc(dr)
        dr_doc.save()
        if int(ecs["Reason Code"]) != 0:
            dr_doc.db_set("workflow_state", "ECS Rejected")
            dr_doc.db_set("ecs_rejection_reason", ecs["Reason description"])
        else:
            dr_doc.submit()
            dr_doc.db_set("workflow_state", "Realized")
            # frappe.db.set_value("Donor", ecs['donor_id'], 'ecs_active', 0)


############ CLOSE ###############
######## ECS DATA PROCESS ########
