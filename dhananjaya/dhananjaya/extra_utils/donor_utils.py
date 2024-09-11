from dhananjaya.dhananjaya.extra_utils.address_process import parseFullAddress
from dhananjaya.dhananjaya.utils import (
    get_formatted_address,
    is_valid_aadhar_number,
    is_valid_pan_number,
)
import frappe, re
from rapidfuzz import fuzz


def find_donor(contact=None, pan_no=None, aadhar_no=None):
    if pan_no:
        pan_no = clean_pan(pan_no)
        pan_donors = frappe.db.sql(
            f"""
                select name
                from `tabDonor`
                where REGEXP_REPLACE(pan_no, '\\s+', '') = '{pan_no}'
                """,
            as_dict=1,
        )
        if len(pan_donors) > 0:
            return pan_donors[0]["name"]

    if aadhar_no:
        aadhar_no = clean_aadhar(aadhar_no)
        aadhar_donors = frappe.db.sql(
            f"""
                select name
                from `tabDonor`
                where REGEXP_REPLACE(aadhar_no, '\\s+', '') = '{aadhar_no}'
                """,
            as_dict=1,
        )
        if len(aadhar_donors) > 0:
            return aadhar_donors[0]["name"]

    if contact:
        contact = clean_contact(contact)
        contacts = frappe.db.sql(
            f"""
                select contact_no,parent
                from `tabDonor Contact`
                where REGEXP_REPLACE(contact_no, '[^0-9]+', '') LIKE '%{contact}%' and parenttype = 'Donor'
                """,
            as_dict=1,
        )
        if len(contacts) > 0:
            return contacts[0]["parent"]

    return None


def check_and_update_donor(
    donor, address=None, contact=None, email=None, pan_no=None, aadhar_no=None
):
    donor_doc = frappe.get_doc("Donor", donor)
    if (
        address and len(address) >= 10
    ):  ### Address should not be very small sized because it will just lead to 100% fuzzy match then
        address_exists = False
        for addr in donor_doc.addresses:
            full_address = get_formatted_address(addr)
            token_ratio = fuzz.token_set_ratio(address, full_address)
            print(token_ratio)
            if token_ratio > 50:
                address_exists = True
                break
        if not address_exists:
            resolved_address = parseFullAddress(address)
            address_single = {
                "type": "Residential",
                "address_line_1": resolved_address[0],
                "city": resolved_address[1],
                "state": resolved_address[2],
                "pin_code": resolved_address[4],
            }
            donor_doc.append("addresses", address_single)

    if contact:
        contact = clean_contact(contact)
        contacts = frappe.db.sql(
            f"""
                select contact_no
                from `tabDonor Contact`
                where REGEXP_REPLACE(contact_no, '[^0-9]+', '') LIKE '%{contact}%' and parenttype = 'Donor' and parent = '{donor_doc.name}'
                """,
            as_dict=1,
        )
        if len(contacts) == 0:
            donor_doc.append("contacts", {"contact_no": contact})

    if email:
        email = clean_email(email)
        emails = frappe.db.sql(
            f"""
                select email
                from `tabDonor Email`
                where email LIKE '%{email}%' and parent = '{donor_doc.name}'
                """,
            as_dict=1,
        )
        if len(emails) == 0:
            donor_doc.append("emails", {"email": email})

    if pan_no:
        pan_no = clean_pan(pan_no)
        if is_valid_pan_number(pan_no) and (
            (not donor_doc.pan_no) or (not is_valid_pan_number(donor_doc.pan_no))
        ):
            donor_doc.pan_no = pan_no

    if aadhar_no:
        aadhar_no = clean_aadhar(aadhar_no)
        if is_valid_aadhar_number(aadhar_no) and (
            (not donor_doc.aadhar_no)
            or (not is_valid_aadhar_number(donor_doc.aadhar_no))
        ):
            donor_doc.aadhar_no = aadhar_no

    donor_doc.save(ignore_permissions=True)
    frappe.db.commit()


def clean_contact(contact):
    return re.sub(r"\D", "", contact)[-10:]


def clean_aadhar(aadhar):
    return re.sub(r"\s+", "", aadhar)


def clean_pan(pan):
    return re.sub(r"\s+", "", pan)


def clean_email(email):
    return re.sub(r"\s+", "", email)
