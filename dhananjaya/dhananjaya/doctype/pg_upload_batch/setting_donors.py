import frappe, json
from dhananjaya.dhananjaya.extra_utils.donor_utils import (
    check_and_update_donor,
    find_donor,
)


@frappe.whitelist()
def try_razorpay_pattern(batch):
    txs = frappe.db.get_list(
        "Payment Gateway Transaction",
        filters={"batch": batch},
        fields=["name", "gateway", "extra_data"],
    )

    for tx in txs:
        notes = json.loads(tx["extra_data"])["notes"]
        notes = json.loads(notes)
        if not notes:
            frappe.throw("Extra Data is not Proper.")
        donor_found = razorpay_identify_and_update_donor(notes)
        if donor_found is None:
            doc = frappe.new_doc("Donor")
            doc.first_name = notes["legal_name"]
            doc.llp_preacher = "DCC"
            doc.save()
            check_and_update_donor(
                donor=doc.name,
                address=notes["address"],
                contact=notes["whatsapp_number"],
                email=notes["email"],
            )
            donor_found = doc.name
        frappe.db.set_value(
            "Payment Gateway Transaction", tx["name"], "donor", donor_found
        )


def razorpay_identify_and_update_donor(notes):
    contact = notes["whatsapp_number"]
    pan_no = None
    if "pan_number" in notes:
        pan_no = notes["pan_number"]

    donor_found = find_donor(contact=contact, pan_no=pan_no)
    if donor_found:
        check_and_update_donor(
            donor=donor_found, pan_no=pan_no, address=notes["address"]
        )
    return donor_found


@frappe.whitelist()
def try_au_qr_pattern(batch):
    txs = frappe.db.get_list(
        "Payment Gateway Transaction",
        filters={"batch": batch},
        fields=["name", "gateway", "extra_data"],
    )

    for tx in txs:
        extra_data = json.loads(tx["extra_data"])
        if not extra_data:
            frappe.throw("Extra Data is not Proper.")

        donor_found = au_qr_identify_and_update_donor(extra_data)

        if donor_found is None:
            doc = frappe.new_doc("Donor")
            doc.first_name = extra_data["Customer Name"]
            doc.llp_preacher = frappe.db.get_single_value(
                "Dhananjaya Settings", "default_preacher"
            )
            doc.save()
            check_and_update_donor(
                donor=doc.name,
                contact=extra_data["Mobile No"],
            )
            donor_found = doc.name
        frappe.db.set_value(
            "Payment Gateway Transaction", tx["name"], "donor", donor_found
        )


def au_qr_identify_and_update_donor(extra_data):
    contact = extra_data["Mobile No"]
    pan_no = None
    if "PAN Number" in extra_data:
        pan_no = extra_data["PAN Number"]
    donor_found = find_donor(contact=contact, pan_no=pan_no)
    if donor_found:
        check_and_update_donor(donor=donor_found, pan_no=pan_no)
    return donor_found


@frappe.whitelist()
def try_standard_pattern(batch):
    txs = frappe.db.get_list(
        "Payment Gateway Transaction",
        filters={"batch": batch},
        fields=["name", "gateway", "extra_data"],
    )

    for tx in txs:
        extra_data = json.loads(tx["extra_data"])
        if not extra_data:
            frappe.throw("Extra Data is not Proper.")

        donor_found = standard_identify_and_update_donor(extra_data)

        if donor_found is None:
            doc = frappe.new_doc("Donor")
            doc.first_name = extra_data["Full Name"]
            doc.llp_preacher = frappe.db.get_single_value(
                "Dhananjaya Settings", "default_preacher"
            )
            doc.save()
            check_and_update_donor(
                donor=doc.name,
                contact=extra_data["Mobile Number"],
                address=extra_data["Address"],
                email=None if "Email" not in extra_data else extra_data["Email"],
                pan_no=(
                    None if "PAN Number" not in extra_data else extra_data["PAN Number"]
                ),
                aadhar_no=(
                    None
                    if "Aadhar Number" not in extra_data
                    else extra_data["Aadhar Number"]
                ),
            )
            donor_found = doc.name
        frappe.db.set_value(
            "Payment Gateway Transaction", tx["name"], "donor", donor_found
        )


def standard_identify_and_update_donor(extra_data):
    contact = extra_data["Mobile Number"]
    pan_no = None
    aadhar_no = None
    address = None
    email = None
    if "PAN Number" in extra_data:
        pan_no = extra_data["PAN Number"]
    if "Aadhar Number" in extra_data:
        aadhar_no = extra_data["Aadhar Number"]
    if "Address" in extra_data:
        address = extra_data["Address"]
    if "Email" in extra_data:
        email = extra_data["Email"]
    donor_found = find_donor(contact=contact, pan_no=pan_no, aadhar_no=aadhar_no)

    if donor_found:
        check_and_update_donor(
            donor=donor_found,
            pan_no=pan_no,
            aadhar_no=aadhar_no,
            address=address,
            email=email,
        )
    return donor_found
