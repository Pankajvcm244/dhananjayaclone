# import frappe
# import re, json
# from frappe.utils import today
# from dhananjaya.dhananjaya.utils import (
#     encode_donation_id,
#     get_company_defaults,
#     get_short_url,
# )
# import pandas as pd
# from frappe.exceptions import InvalidEmailAddressError

# from dhananjaya.api.v1.direct.address_process import parseFullAddress
# from dhananjaya.api.v1.direct.identify import identify_donor

# # Define pre-declared variables for dictionary keys
# F_DONATION = "donation"
# F_PREACHER = "preacher"
# F_RECEIPT_SERIES = "receipt_series"
# F_DEFAULT_MARKETING_PREACHER = "default_marketing_preacher"
# F_PAN_NO = "pan_no"
# F_AADHAR_NO = "aadhar_no"
# F_MOBILE = "mobile"
# F_DONOR_NAME = "donor_name"
# F_ADDRESS = "address"
# F_EMAIL = "email"
# F_COMPANY = "company"
# F_PAYMENT_METHOD = "payment_method"
# F_AMOUNT = "amount"
# F_REMARKS = "remarks"
# F_SEVA_TYPE = "seva_type"
# F_SEVA_SUBTYPE = "seva_subtype"
# F_DR_NO = "dr_no"
# F_ADDITIONAL_CHARGES = "additional_charges"
# F_PRINT_REMARKS_ON_RECEIPT = "print_remarks_on_receipt"
# F_ATG_REQUIRED = "atg_required"
# F_SEPARATED_ADDRESS = "separated_address"
# F_RECEIPT_DATE = "Receipt_date"


# def read_excel_file():
#     file_path = "/home/ubuntu/frappe-bench/apps/dhananjaya/dhananjaya/SFC Data by DCC FY 2024-25.xlsx"
#     json_data = None
#     try:
#         # Read the Excel file into a DataFrame
#         df = pd.read_excel(file_path)
#         # Convert DataFrame to JSON
#         df = df.fillna("")
#         df = df.astype(str)
#         df["amount"] = pd.to_numeric(df["amount"])
#         json_data = df.to_json(orient="records")
#         json_data = json.loads(json_data)
#     except Exception as e:
#         print("Error reading Excel file:", e)
#         return None

#     if json_data:
#         for ind, data in enumerate(json_data):
#             # if 316 < ind <= 5000:
#             if ind > 0:
#                 # print(data)
#                 # if ind == 142:
#                 print(f"Proceesing Receipt Number {ind+1}")
#                 upload_donation(data)


# # @frappe.whitelist(methods=["POST"])
# def upload_donation(data):
#     donation_raw = data

#     # if frappe.db.exists("Donation Receipt", {"old_dr_no": data["dr_no"]}):
#     #     return

#     preacher = donation_raw[F_PREACHER]

#     if not frappe.db.exists("LLP Preacher", preacher):
#         preacher_doc = frappe.get_doc(
#             {"doctype": "LLP Preacher", "full_name": preacher, "initial": preacher}
#         )
#         preacher_doc.insert()

#     clean_contact = re.sub(r"\D", "", donation_raw.get(F_MOBILE, ""))[-10:]
#     clean_pan = re.sub(r"\s+", "", donation_raw.get(F_PAN_NO, ""))
#     clean_aadhar = re.sub(r"\s+", "", donation_raw.get(F_AADHAR_NO, ""))
#     donor = identify_donor(
#         contact=clean_contact, email=None, pan=clean_pan, aadhar=clean_aadhar
#     )  # We don't wish to identify a donor by email.

#     rec_address = {
#         "type": "Residential",
#         "address_line_1": (
#             data["address_line_1"][:100]
#             if len(data["address_line_1"]) > 100
#             else data["address_line_1"]
#         ),
#         "address_line_2": data["address_line_2"],
#         "city": data["city"],
#         "state": data["state"],
#         "country": "India",
#         "pin_code": data["pin_code"],
#     }

#     if donor is None:
#         donor_dict = {
#             "doctype": "Donor",
#             "first_name": donation_raw.get(F_DONOR_NAME),
#             "llp_preacher": preacher,
#         }

#         # rec_address_str = (
#         #     data["address_line_1"]
#         #     + (" " + data["address_line_2"] if data["address_line_2"] else "")
#         #     + (" " + data["city"] if data["city"] else "")
#         #     + (" " + data["state"] if data["state"] else "")
#         #     + " India"
#         #     + ("-" + data["pin_code"] if data["pin_code"] else "")
#         # )

#         clean_email = donation_raw[F_EMAIL] if donation_raw[F_EMAIL] != "0" else None
#         donor_dict.update({"addresses": [rec_address]})
#         if clean_email:
#             donor_dict.update({"emails": [{"email": clean_email}]})

#         if clean_contact:
#             donor_dict.update({"contacts": [{"contact_no": clean_contact}]})

#         if clean_pan:
#             donor_dict.update({"pan_no": clean_pan})

#         if clean_aadhar:
#             donor_dict.update({"aadhar_no": clean_aadhar})

#         try:
#             donor_doc = frappe.get_doc(donor_dict)
#             donor_doc.insert(ignore_permissions=True)
#         except InvalidEmailAddressError:
#             del donor_dict["emails"]
#             donor_doc = frappe.get_doc(donor_dict)
#             donor_doc.insert(ignore_permissions=True)

#         donor = donor_doc.name
#     else:
#         ## Update Data If Donor is identified
#         donor_doc = frappe.get_doc("Donor", donor)
#         if clean_pan and not donor_doc.pan_no:
#             donor_doc.pan_no = clean_pan

#         if clean_aadhar and not donor_doc.aadhar_no:
#             donor_doc.aadhar_no = clean_aadhar

#         if len(donor_doc.contacts) == 0:
#             donor_doc.append("contacts", {"contact_no": clean_contact})

#         if len(donor_doc.addresses) == 0:
#             donor_doc.append("addresses", rec_address)

#         donor_doc.save(ignore_permissions=True)
#         donor = donor_doc.name
#         preacher = donor_doc.llp_preacher

#     receipt_dict = {
#         "doctype": "Donation Receipt",
#         "receipt_series": ".company_abbreviation.-SFC-.####",
#         "receipt_date": donation_raw.get(F_RECEIPT_DATE),
#         "company": donation_raw.get(F_COMPANY),
#         "preacher": preacher,
#         "donor": donor,
#         "payment_method": donation_raw.get(F_PAYMENT_METHOD),
#         "amount": donation_raw.get(F_AMOUNT),
#         "remarks": donation_raw.get(F_REMARKS),
#         "seva_type": donation_raw.get(F_SEVA_TYPE),
#         "seva_subtype": donation_raw.get(F_SEVA_SUBTYPE),
#         "old_dr_no": donation_raw.get(F_DR_NO),
#         "print_remarks_on_receipt": 1,
#         "atg_required": 1 if donation_raw[F_ATG_REQUIRED] == "Yes" else 0,
#         "auto_generated": 1,
#     }

#     receipt_doc = frappe.get_doc(receipt_dict)
#     receipt_doc.insert(ignore_permissions=True)

#     receipt_doc.db_set("workflow_state", "Acknowledged")
#     # receipt_doc.db_set("docstatus", 1)

#     frappe.db.commit()
