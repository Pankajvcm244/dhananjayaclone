# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

from dhananjaya.dhananjaya.utils import (
    get_donor_details,
    is_valid_pan_number,
    is_valid_aadhar_number,
)
import frappe
from frappe.model.document import Document


class DonorCreationRequest(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        aadhar_number: DF.Data | None
        address_line_1: DF.Data
        address_line_2: DF.Data | None
        address_type: DF.Literal["Residential", "Office", "Other"]
        amended_from: DF.Link | None
        city: DF.Data
        contact_number: DF.Data
        email: DF.Data | None
        full_name: DF.Data
        latitude: DF.Float
        llp_preacher: DF.Link | None
        longitude: DF.Float
        pan_number: DF.Data | None
        pin_code: DF.Data | None
        state: DF.Literal[
            "",
            "Andaman and Nicobar Islands",
            "Andhra Pradesh",
            "Arunachal Pradesh",
            "Assam",
            "Bihar",
            "Chandigarh",
            "Chhattisgarh",
            "Dadra and Nagar Haveli and Daman and Diu",
            "Delhi",
            "Goa",
            "Gujarat",
            "Haryana",
            "Himachal Pradesh",
            "Jammu and Kashmir",
            "Jharkhand",
            "Karnataka",
            "Kerala",
            "Ladakh",
            "Lakshadweep Islands",
            "Madhya Pradesh",
            "Maharashtra",
            "Manipur",
            "Meghalaya",
            "Mizoram",
            "Nagaland",
            "Odisha",
            "Other Territory",
            "Pondicherry",
            "Punjab",
            "Rajasthan",
            "Sikkim",
            "Tamil Nadu",
            "Telangana",
            "Tripura",
            "Uttar Pradesh",
            "Uttarakhand",
            "West Bengal",
        ]
        status: DF.Literal["Draft", "Closed", "Open", "Rejected"]

    # end: auto-generated types
    def on_submit(self):
        self.db_set("status", "Open", commit=True)
        frappe.db.commit()

    def validate(self):
        # if not (self.pan_number or self.aadhar_number):
        #     frappe.throw("At least one of PAN or Aadhar is required.")

        if self.pan_number and not is_valid_pan_number(self.pan_number):
            frappe.throw("PAN Number is invalid")

        if self.aadhar_number and not is_valid_aadhar_number(self.aadhar_number):
            frappe.throw("Aadhar Number is invalid.")


@frappe.whitelist()
def get_donor_from_request(request):
    if not is_user_allowed():
        frappe.throw("You are not allowed.")
    request = frappe.get_doc("Donor Creation Request", request)

    addresses = []
    addresses.append(
        {
            "preferred": 1,
            "type": request.address_type,
            "address_line_1": request.address_line_1,
            "address_line_2": request.address_line_2,
            "city": request.city,
            "state": request.state,
            "country": "India",
            "pin_code": request.pin_code,
            "longitude": request.longitude,
            "latitude": request.latitude,
        }
    )

    contacts = []
    contacts.append(
        {
            "contact_no": request.contact_number,
            "is_whatsapp": 1,
        }
    )
    emails = []
    if request.email:
        emails = []
        emails.append({"email": request.email})
    first_name, last_name = get_first_and_last_names(request.full_name)
    donor_dict = {
        "first_name": first_name,
        "last_name": last_name,
        "llp_preacher": request.llp_preacher,
        "addresses": addresses,
        "contacts": contacts,
        "emails": emails,
        "pan_no": request.pan_number,
        "aadhar_no": request.aadhar_number,
        "donor_creation_request": request.name,
    }
    donor_entry = frappe.new_doc("Donor")
    donor_entry.update(donor_dict)
    # donor_entry.set("accounts", accounts)
    return donor_entry


def get_first_and_last_names(full_name):
    splitted = full_name.split(" ", 1)
    if len(splitted) > 1:
        first_name, last_name = splitted
        if len(first_name) > 3:
            return first_name, last_name
    first_name, last_name = full_name, ""
    return first_name, last_name


@frappe.whitelist()
def get_similar_donors(request):
    results = {"first": {}, "second": {}}

    import re

    request = frappe.get_doc("Donor Creation Request", request)
    similar_found = []
    if request.contact_number:
        clean_contact = re.sub(r"\D", "", request.contact_number)[-10:]
        contacts = frappe.db.sql(
            f"""
				select contact_no,parent
				from `tabDonor Contact`
				where REGEXP_REPLACE(contact_no, '[^0-9]+', '') LIKE '%{clean_contact}%' and parenttype = 'Donor'
				""",
            as_dict=1,
        )
        if len(contacts) > 0:
            for c in contacts:
                similar_found.append(c["parent"])

    if request.email:
        emails = frappe.db.sql(
            f"""
				select email,parent
				from `tabDonor Email`
				where email LIKE '%{request.email.strip()}%' and parenttype = 'Donor'
				""",
            as_dict=1,
        )
        if len(emails) > 0:
            for e in emails:
                similar_found.append(e["parent"])

    if request.pan_number:
        clean_pan = request.pan_number.replace(" ", "")
        donors = frappe.db.sql(
            f"""
				select name
				from `tabDonor`
				where pan_no = '%{clean_pan}%'
				""",
            as_dict=1,
        )
        if len(donors) > 0:
            for d in donors:
                similar_found.append(d["name"])

    if request.aadhar_number:
        clean_aadhar = request.aadhar_number.replace(" ", "")
        donors = frappe.db.sql(
            f"""
				select name
				from `tabDonor`
				where aadhar_no = '%{clean_aadhar}%'
				""",
            as_dict=1,
        )
        if len(donors) > 0:
            for d in donors:
                similar_found.append(d["name"])

    similar_found = list(set(similar_found))
    if len(similar_found) > 0:
        results["first"] = get_donor_details(similar_found)
        # # for i in frappe.db.sql(f"""
        # # 				select name,full_name
        # # 				from `tabDonor`
        # # 				where name IN ({similar_found_string})
        # # 				""", as_dict=1):
        #     results['first'][i['name']] = i

    #################################
    # Try for Similar matches in Names
    #################################

    similar_found = []
    for i in frappe.db.sql(
        f"""
					select name
					from `tabDonor`
					where full_name LIKE '%{request.full_name}%'
                    limit 10
					""",
        as_dict=1,
    ):
        similar_found.append(i["name"])

    if len(similar_found) > 0:
        results["second"] = get_donor_details(similar_found)

    return results


def is_user_allowed():
    ALLOWED_ROLES = ["DCC Executive", "DCC Manager"]
    user_roles = frappe.get_roles(frappe.session.user)

    for role in ALLOWED_ROLES:
        if role in user_roles:
            return True
    return False


@frappe.whitelist()
def update_donor(donor, request):
    if not is_user_allowed():
        frappe.throw("You are not allowed.")

    request_doc = frappe.get_doc("Donor Creation Request", request)
    frappe.db.set_value("Donor Creation Request", request, "status", "Closed")
    donations = frappe.get_all(
        "Donation Receipt", filters={"donor_creation_request": request}, pluck="name"
    )
    donor = frappe.get_doc("Donor", donor)
    for d in donations:
        frappe.db.set_value(
            "Donation Receipt",
            d,
            {
                "donor": donor.name,
                "full_name": donor.full_name,
                "preacher": donor.llp_preacher,
            },
        )
    frappe.db.commit()
    title = "Donor Creation Rejected!"
    message = f"Your donor request with name {request_doc.full_name}({request}) was NOT considered as this Donor is already existing with the name {donor.full_name}({donor.name}). Please contact DCC Admin for any conflicts."
    data = {"route": "true", "target_route": f"/donor/{donor.name}"}

    erp_user = request_doc.owner
    settings_doc = frappe.get_cached_doc("Dhananjaya Settings")
    doc = frappe.get_doc(
        {
            "doctype": "App Notification",
            "app": settings_doc.firebase_admin_app,
            "channel": settings_doc.donor_creation_channel,
            "user": erp_user,
            "subject": title,
            "message": message,
            "is_route": 1,
            "route": f"/donor/{donor.name}",
        }
    )
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
