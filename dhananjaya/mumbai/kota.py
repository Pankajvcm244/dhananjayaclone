import json
import re
from dhananjaya.dhananjaya.utils import get_best_contact_address
import frappe


@frappe.whitelist()
def set_donation_found():
    for t in frappe.get_all("Temp Data", fields=["*"]):
        donation_matchs = frappe.db.sql(
            f"""
                        select *
                        from `tabDonation Receipt`
                        where REGEXP_REPLACE(contact, '[^0-9]+', '') like '%{t["mobile"]}%'
                        and amount = {t["amount"]}
                        and receipt_date BETWEEN DATE_SUB('{t['date']}', INTERVAL 2 DAY) AND DATE_ADD('{t['date']}', INTERVAL 2 DAY);
                            """,
            as_dict=1,
        )
        if len(donation_matchs) > 0:
            frappe.db.set_value(
                "Temp Data", t["name"], "donation_receipt", donation_matchs[0]["name"]
            )
    frappe.db.commit()


@frappe.whitelist()
def create_direct_receipt():
    t = frappe.request.data
    t = json.loads(t)
    receipt_dict = t
    workflow = receipt_dict["workflow_state"]
    del receipt_dict["workflow_state"]
    receipt_doc = frappe.get_doc(receipt_dict)
    receipt_doc.insert(ignore_permissions=True, ignore_mandatory=True)
    receipt_doc.db_set("workflow_state", workflow)
    receipt_doc.db_set("docstatus", 1)
    frappe.db.commit()


@frappe.whitelist()
def create_receipt():
    t = frappe.request.data
    t = json.loads(t)
    donor = check_donor_or_create(t)
    llp_preacher = frappe.db.get_value("Donor", donor, "llp_preacher")
    receipt_dict = {
        "doctype": "Donation Receipt",
        "company": t["company"],
        "receipt_date": t["receipt_date"],
        "preacher": llp_preacher,
        "donor": donor,
        "contact": t["mobile"],
        "address": t["address"],
        "payment_method": t["payment_method"],
        "amount": t["amount"],
        "remarks": t["remarks"],
        "seva_type": t["seva_type"],
        "old_dr_no": t["old_dr_no"],
        "full_name": t["full_name"],
    }

    if "additional_charges" in t:
        receipt_dict["additional_charges"] = t["additional_charges"]

    receipt_doc = frappe.get_doc(receipt_dict)
    receipt_doc.insert(ignore_permissions=True)

    # if "status" in t and t["status"] == "Acknowledged":
    #     receipt_doc.db_set("workflow_state", t['status'])
    #     receipt_doc.db_set("docstatus", 0)
    # elif "status" not in t or t["status"] in ["Realized","Received by Cashier"]:
    #     if t["mode_of_payment"]  == "Cash":
    #         receipt_doc.db_set("workflow_state", "Received by Cashier")
    #     else:
    #         receipt_doc.db_set("workflow_state", "Realized")
    #     receipt_doc.db_set("docstatus", 1)
    # else:
    #     frappe.throw('Status can only be one of ["Acknowledged", "Realized","Received by Cashier"]')

    # if not frappe.db.exists({"doctype": "Devotee", "name1": receipt_doc.preacher}):
    #     devotee_doc = frappe.get_doc({
    #         "doctype":"Devotee",
    #         "name1":receipt_doc.preacher
    #     })
    #     devotee_doc.insert()
    #     frappe.db.commit()

    receipt_doc.db_set("workflow_state", "Realized")
    receipt_doc.db_set("docstatus", 1)

    # je_dict = {
    #                 "docstatus":1,
    #                 "doctype":"Journal Entry",
    #                 # "voucher_type":"Journal Entry",
    #                 "naming_series":"ACC-JV-.YYYY.-",
    #                 "company":"Kota - Hare Krishna Movement",
    #                 "posting_date":f"{t['date']}",
    #                 "donation_receipt":receipt_doc.name,
    #                 "cheque_no":t['transaction_id'],
    #                 "cheque_date":f"{t['date']}",
    #                 "user_remark":f"BEING AMOUNT RECEIVED FOR General Donation - K-HKM FROM {t['donor_name']} AS PER R.NO. {receipt_doc.name} DT. {t['date']} DCC",
    #                 "accounts":
    #                     [
    #                         {
    #                             "account":"Donation Income-India - K-HKM",
    #                             "devotee": "DCC",
    #                             "cost_center":"General donation - K-HKM",
    #                             "debit_in_account_currency":0,
    #                             "debit":0,
    #                             "credit_in_account_currency":t["amount"],
    #                             "credit":t["amount"],
    #                             "is_a_donation":1,
    #                             "dr_no":receipt_doc.name,
    #                             "donor_name":t['donor_name'],
    #                             "receipt_date":f"{t['date']}",
    #                         },
    #                         {
    #                             "account":"Suspense - K-HKM",
    #                             "cost_center":"Main - K-HKM",
    #                             "debit_in_account_currency":t["amount"],
    #                             "debit":t["amount"],
    #                             "credit_in_account_currency":0,
    #                             "credit":0,
    #                         },
    #                     ],
    #             }

    # je_doc = frappe.get_doc(je_dict)
    # je_doc.insert(ignore_permissions=True)

    # receipt_doc.db_set("temp_je", je_doc.name)

    frappe.db.commit()

    return {"receipt_id": receipt_doc.name, "donor_id": donor}


@frappe.whitelist()
def create_receipt_from_bank_suspense():
    t = frappe.request.data
    t = json.loads(t)
    donor = t["donor"]
    llp_preacher = frappe.db.get_value("Donor", donor, "llp_preacher")
    address, contact, _ = get_best_contact_address(t["donor"])
    receipt_dict = {
        "doctype": "Donation Receipt",
        "company": "Kota - Hare Krishna Movement",
        "receipt_date": t["date"],
        "preacher": llp_preacher,
        "donor": donor,
        "contact": address,
        "address": contact,
        "payment_method": t["mode_of_payment"],
        "amount": t["amount"],
        "remarks": t["remarks"],
        "seva_type": "General Donation - K-HKM",
        # "old_dr_no": t["dr_no"],
    }

    if "additional_charges" in t:
        receipt_dict["additional_charges"] = t["additional_charges"]

    receipt_doc = frappe.get_doc(receipt_dict)
    receipt_doc.insert(ignore_permissions=True)

    # if "status" in t and t["status"] == "Acknowledged":
    #     receipt_doc.db_set("workflow_state", t['status'])
    #     receipt_doc.db_set("docstatus", 0)
    # elif "status" not in t or t["status"] in ["Realized","Received by Cashier"]:
    #     if t["mode_of_payment"]  == "Cash":
    #         receipt_doc.db_set("workflow_state", "Received by Cashier")
    #     else:
    #         receipt_doc.db_set("workflow_state", "Realized")
    #     receipt_doc.db_set("docstatus", 1)
    # else:
    #     frappe.throw('Status can only be one of ["Acknowledged", "Realized","Received by Cashier"]')

    # if not frappe.db.exists({"doctype": "Devotee", "name1": receipt_doc.preacher}):
    #     devotee_doc = frappe.get_doc({
    #         "doctype":"Devotee",
    #         "name1":receipt_doc.preacher
    #     })
    #     devotee_doc.insert()
    #     frappe.db.commit()

    receipt_doc.db_set("workflow_state", "Realized")
    receipt_doc.db_set("docstatus", 1)

    je_dict = {
        "docstatus": 1,
        "doctype": "Journal Entry",
        # "voucher_type":"Journal Entry",
        "naming_series": "ACC-JV-.YYYY.-",
        "company": "Kota - Hare Krishna Movement",
        "posting_date": f"{t['date']}",
        "donation_receipt": receipt_doc.name,
        # "cheque_no":t['transaction_id'],
        # "cheque_date":f"{t['date']}",
        "user_remark": f"BEING AMOUNT RECEIVED FOR General Donation - K-HKM FROM {receipt_doc.full_name} AS PER R.NO. {receipt_doc.name} DT. {t['date']} DCC",
        "accounts": [
            {
                "account": "Donation Income-India - K-HKM",
                "devotee": "DCC",
                "cost_center": "General donation - K-HKM",
                "debit_in_account_currency": 0,
                "debit": 0,
                "credit_in_account_currency": t["amount"],
                "credit": t["amount"],
                "is_a_donation": 1,
                "dr_no": receipt_doc.name,
                "donor_name": receipt_doc.full_name,
                "receipt_date": f"{t['date']}",
            },
            {
                "account": "Suspense - K-HKM",
                "cost_center": "Main - K-HKM",
                "debit_in_account_currency": t["amount"],
                "debit": t["amount"],
                "credit_in_account_currency": 0,
                "credit": 0,
                "suspense_jv": t["suspense_jv"],
            },
        ],
    }

    je_doc = frappe.get_doc(je_dict)
    je_doc.insert(ignore_permissions=True)

    receipt_doc.db_set("temp_je", je_doc.name)

    frappe.db.commit()

    return {"receipt_id": receipt_doc.name, "donor_id": donor}


def check_donor_or_create(t):
    donor = None
    clean_contact = None
    if t["mobile"]:
        t["mobile"] = str(t["mobile"])
        clean_contact = re.sub(r"\D", "", t["mobile"])[-10:]
        contacts = frappe.db.sql(
            f"""
                select contact_no,parent
                from `tabDonor Contact`
                where REGEXP_REPLACE(contact_no, '[^0-9]+', '') LIKE '%{clean_contact}%' and parenttype = 'Donor'
                """,
            as_dict=1,
        )
        if len(contacts) > 0:
            donor = contacts[0]["parent"]

    if donor is None:
        donor_dict = {
            "doctype": "Donor",
            "first_name": t["donor_name"],
            "llp_preacher": t["preacher"],
        }

        if t["address"]:
            # resolved_address = parseFullAddress(t["address"])

            address_single = [
                {
                    "address_line_1": "Jaipur",
                    "city": "Jaipur",
                    "state": "Rajasthan"
                    # "pin_code": resolved_address[4],
                }
            ]

            donor_dict.update({"addresses": address_single})

        # if ("email" in t) and t["email"]:
        #     donor_dict.update({"emails": [{
        #         'email':t['email']
        #     }]})

        if clean_contact is not None:
            donor_dict.update({"contacts": [{"contact_no": clean_contact}]})

        # if clean_pan is not None:
        #     donor_dict.update({"pan_no": clean_pan})

        donor_doc = frappe.get_doc(donor_dict)

        donor_doc.insert()

        donor = donor_doc.name

    return donor
