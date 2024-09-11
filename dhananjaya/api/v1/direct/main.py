# from hkm.erpnext___custom.doctype.hkm_api_call.hkm_api_call import store_incoming_api
import frappe
import re, json
from frappe.utils import today
from dhananjaya.dhananjaya.utils import (
    encode_donation_id,
    get_company_defaults,
    get_short_url,
)

from dhananjaya.api.v1.direct.address_process import parseFullAddress
from dhananjaya.api.v1.direct.identify import identify_donor, identify_patron

# Define pre-declared variables for dictionary keys
F_DONATION = "donation"
F_PREACHER = "preacher"
F_RECEIPT_SERIES = "receipt_series"
F_DEFAULT_MARKETING_PREACHER = "default_marketing_preacher"
F_PAN_NO = "pan_no"
F_AADHAR_NO = "aadhar_no"
F_MOBILE = "mobile"
F_DONOR_NAME = "donor_name"
F_ADDRESS = "address"
F_EMAIL = "email"
F_COMPANY = "company"
F_PAYMENT_METHOD = "payment_method"
F_AMOUNT = "amount"
F_REMARKS = "remarks"
F_SEVA_TYPE = "seva_type"
F_SEVA_SUBTYPE = "seva_subtype"
F_DR_NO = "dr_no"
F_ADDITIONAL_CHARGES = "additional_charges"
F_PRINT_REMARKS_ON_RECEIPT = "print_remarks_on_receipt"
F_ATG_REQUIRED = "atg_required"
F_SEPARATED_ADDRESS = "separated_address"
F_RECEIPT_DATE = "receipt_date"
F_TRY_PATRONSHIP_TAGGING = "try_patron_tagging"


@frappe.whitelist(methods=["POST"])
def upload_donation():
    # store_incoming_api()
    try:
        data = json.loads(frappe.request.data)

        if data.get(F_DONATION) is None:
            frappe.throw("Please send some data")

        donation_raw = data.get(F_DONATION)
    except Exception as e:
        print(e)
        frappe.throw("Receipt Data Format is Incorrect.")

    validate(donation_raw)

    # Preacher Identify
    try:
        donation_raw[F_PREACHER] = donation_raw.get(F_PREACHER).strip()
        preacher = frappe.get_doc("LLP Preacher", donation_raw[F_PREACHER]).name
    except:
        preacher = frappe.db.get_single_value(
            "Dhananjaya Settings", F_DEFAULT_MARKETING_PREACHER
        )
        if preacher is None:
            frappe.throw(
                "Please set the default Marketing Preacher in Dhananajaya Settings first."
            )

    clean_contact = donation_raw.get(F_MOBILE, "")
    # clean_contact = re.sub(r"\D", "", donation_raw.get(F_MOBILE, "")) ## As there are international numbers also received
    # clean_email = None
    # if "email" in donation_raw:
    #     clean_email = re.sub(r"\s+", "", donation_raw.get(F_EMAIL, ""))
    clean_pan = re.sub(r"\s+", "", donation_raw.get(F_PAN_NO, ""))
    clean_aadhar = re.sub(r"\s+", "", donation_raw.get(F_AADHAR_NO, ""))

    resolved_address = get_address(donation_raw)

    donor = identify_donor(
        full_name_received=donation_raw.get(F_DONOR_NAME),
        contact=clean_contact,
        email=None,
        pan=clean_pan,
        aadhar=clean_aadhar,
    )  # We don't wish to identify a donor by email.

    patron = None
    if donation_raw.get(F_TRY_PATRONSHIP_TAGGING):
        patron = identify_patron(
            contact=clean_contact, email=None, pan=clean_pan, aadhar=clean_aadhar
        )

    if donor is None:
        donor_dict = {
            "doctype": "Donor",
            "first_name": donation_raw.get(F_DONOR_NAME),
            "llp_preacher": preacher,
        }

        donor_dict.update({"addresses": [resolved_address]})

        if donation_raw.get(F_EMAIL):
            donor_dict.update({"emails": [{"email": donation_raw[F_EMAIL]}]})

        if clean_contact:
            donor_dict.update({"contacts": [{"contact_no": clean_contact}]})

        if clean_pan:
            donor_dict.update({"pan_no": clean_pan})

        if clean_aadhar:
            donor_dict.update({"aadhar_no": clean_aadhar})

        donor_doc = frappe.get_doc(donor_dict)

        donor_doc.insert(ignore_permissions=True)

        donor = donor_doc.name
    else:
        ## Update Data If Donor is identified
        donor_doc = frappe.get_doc("Donor", donor)
        if clean_pan and not donor_doc.pan_no:
            donor_doc.pan_no = clean_pan

        if clean_aadhar and not donor_doc.aadhar_no:
            donor_doc.aadhar_no = clean_aadhar

        if len(donor_doc.contacts) == 0:
            donor_doc.append("contacts", {"contact_no": clean_contact})

        if len(donor_doc.addresses) == 0:
            donor_doc.append("addresses", resolved_address)

        donor_doc.save(ignore_permissions=True)
        donor = donor_doc.name

    # Upload Receipt
    llp_preacher = frappe.db.get_value("Donor", donor, "llp_preacher")

    receipt_dict = {
        "doctype": "Donation Receipt",
        "company": donation_raw.get(F_COMPANY),
        "preacher": llp_preacher,
        "donor": donor,
        "patron": patron,
        "contact": clean_contact,
        # "address": resolved_address, # Address will be automatically fectched from Donor on Save
        # get_formatted_address(frappe._dict(resolved_address)),
        "payment_method": donation_raw.get(F_PAYMENT_METHOD),
        "amount": donation_raw.get(F_AMOUNT),
        "remarks": donation_raw.get(F_REMARKS),
        "seva_type": donation_raw.get(F_SEVA_TYPE),
        "seva_subtype": donation_raw.get(F_SEVA_SUBTYPE),
        "old_dr_no": donation_raw.get(F_DR_NO),
        "additional_charges": donation_raw.get(F_ADDITIONAL_CHARGES),
        "print_remarks_on_receipt": donation_raw.get(F_PRINT_REMARKS_ON_RECEIPT),
        "atg_required": donation_raw.get(F_ATG_REQUIRED),
        "auto_generated": 1,
    }

    ## Set Accounting Dimensions

    if donation_raw.get("project"):
        receipt_dict["project"] = donation_raw.get("project")

    ##

    if donation_raw.get(F_RECEIPT_DATE):
        receipt_dict["receipt_date"] = donation_raw.get(F_RECEIPT_DATE)
    else:
        receipt_dict["receipt_date"] = today()

    if donation_raw.get(F_RECEIPT_SERIES):
        receipt_dict["receipt_series"] = donation_raw.get(F_RECEIPT_SERIES)

    receipt_doc = frappe.get_doc(receipt_dict)
    receipt_doc.insert(ignore_permissions=True)

    receipt_doc.db_set("workflow_state", "Acknowledged")
    # receipt_doc.db_set("docstatus", 0)

    # defaults = get_company_defaults(donation_raw.get(F_COMPANY))

    # if not defaults.auto_create_journal_entries:
    #     if donation_raw[F_PAYMENT_METHOD] == "Cash":
    #         receipt_doc.db_set("workflow_state", "Received by Cashier")
    #     else:
    #         receipt_doc.db_set("workflow_state", "Realized")
    #     receipt_doc.db_set("docstatus", 1)

    frappe.db.commit()

    receipt_token = encode_donation_id(receiptId=receipt_doc.name)

    long_url = (
        "https://"
        + frappe.local.site
        + f"/api/method/dhananjaya.dhananjaya.utils.download_pdf_public?receiptToken={receipt_token}"
    )

    return frappe._dict(
        url=long_url,
        receipt={
            "receipt_id": receipt_doc.name,
            "company": receipt_doc.company,
            "preacher": receipt_doc.preacher,
            "donor_id": receipt_doc.donor,
            "full_name": receipt_doc.full_name,
            "contact": receipt_doc.contact,
            "address": receipt_doc.address,
            "amount": receipt_doc.amount,
            "seva_type": receipt_doc.seva_type,
            "seva_subtype": receipt_doc.seva_subtype,
            "receipt_date": receipt_doc.receipt_date,
        },
    )


COMPULSORY_FIELDS = [
    F_MOBILE,
    F_DONOR_NAME,
    F_COMPANY,
    F_PAYMENT_METHOD,
    F_AMOUNT,
    F_SEVA_TYPE,
]


def validate(donation_raw):
    for cf in COMPULSORY_FIELDS:
        if not donation_raw.get(cf):
            frappe.throw(f"API Request is incomplete. {cf} is a compulsory field.")

    if not (donation_raw.get(F_ADDRESS) or donation_raw.get(F_SEPARATED_ADDRESS)):
        frappe.throw("At least one of Address or Separated Address is required.")
    return


def get_address(donation_raw):
    if donation_raw.get(F_SEPARATED_ADDRESS):
        return donation_raw.get(F_SEPARATED_ADDRESS)
    else:
        resolved_address = parseFullAddress(donation_raw[F_ADDRESS])
        return {
            "type": "Residential",
            "address_line_1": resolved_address[0],
            "city": resolved_address[1],
            "state": resolved_address[2],
            "pin_code": resolved_address[4],
        }
    return address
