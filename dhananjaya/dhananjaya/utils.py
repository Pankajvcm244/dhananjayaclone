import frappe
from frappe import _
import re
from frappe.utils.pdf import get_pdf
from frappe import local
from cryptography.fernet import Fernet


@frappe.whitelist()
def get_short_url(long_url):
    doc = frappe.get_doc({"doctype": "HKM Redirect", "redirect_to": long_url})
    doc.insert()
    frappe.db.commit()
    short_url = local.request.host_url + "sl/" + doc.name
    return short_url


@frappe.whitelist()
def encode_donation_id(receiptId):
    # donation_doc = frappe.get_doc("Donation Receipt", receiptId)
    settings = frappe.get_doc("Dhananjaya Settings")

    if not settings.public_fernet_key:
        key = Fernet.generate_key()
        frappe.db.set_value(
            "Dhananjaya Settings",
            "Dhananjaya Settings",
            "public_fernet_key",
            key.decode(),
        )
        frappe.db.commit()
    else:
        key = settings.public_fernet_key.encode()

    f = Fernet(key)

    token = f.encrypt(receiptId.encode())
    return token.decode()


## This returns the preachers assigned to a User
@frappe.whitelist()
def get_preachers(user=None):
    if not user:
        user = frappe.session.user
    preachers = []
    for i in frappe.db.sql(
        f"""
                    select p.name
                    from `tabLLP Preacher` p
                    join `tabLLP Preacher User` pu
                    on p.name = pu.parent
                    where pu.user = '{user}'
                    group by p.name
                    """,
        as_dict=1,
    ):
        preachers.append(i["name"])
    return preachers


## This returns the Users, the preacher is assigned to.
@frappe.whitelist()
def get_preacher_users(preacher):
    ## PRCH_REMAP
    users = []

    for i in frappe.db.sql(
        f"""
                    select pu.user
                    from `tabLLP Preacher` p
                    join `tabLLP Preacher User` pu
                    on p.name = pu.parent
                    where p.name = '{preacher}'
                    group by pu.user
                    """,
        as_dict=1,
    ):
        users.append(i["user"])
    return users


@frappe.whitelist()
def get_default_bank_account(company):
    doc = frappe.get_cached_doc("Dhananjaya Settings")
    for d in doc.defaults:
        if d.company == company:
            return d.bank_account
    return None


@frappe.whitelist()
def get_default_income_account(company):
    doc = frappe.get_cached_doc("Dhananjaya Settings")
    for d in doc.defaults:
        if d.company == company:
            return d.donation_account
    return None


@frappe.whitelist()
def get_company_defaults(company):
    doc = frappe.get_cached_doc("Dhananjaya Settings")
    for d in doc.company_details:
        if d.company == company:
            return d
    return None


def extract_longest_digits(string):
    digits = re.findall(r"\d+", string)
    longest_digits = max(digits, key=len)
    return longest_digits


def is_valid_pan_number(pan):
    pan_pattern = re.compile("[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}")
    if pan_pattern.fullmatch(pan):
        return True
    return False


def is_valid_aadhar_number(aadhar_number):
    # regex pattern for aadhar number
    aadhar_pattern = re.compile(r"^\d{12}$")

    # check if aadhar number matches the pattern
    if aadhar_pattern.match(aadhar_number):
        return True
    return False


def is_valid_pincode(pinCode):
    return True
    # Regex to check valid pin code of India.
    # TODO check pincode Validity
    regex = "^[1-9]{1}[0-9]{2}\\s{0,1}[0-9]{3}$"
    p = re.compile(regex)
    m = re.match(p, pinCode)
    if m is None:
        return False
    else:
        return True


def get_receipt_filename(doc):
    return "{donor_name} - {receipt_no}.pdf".format(
        donor_name=(
            doc.full_name if doc.full_name else doc.donor_creation_request_name
        ).strip(),
        receipt_no=doc.name.replace(" ", "-").replace("/", "-"),
    )


def get_receipt_content(doc):
    settings = frappe.get_cached_doc("Dhananjaya Settings")
    seva_type_specific_format = frappe.db.get_value(
        "Seva Type", doc.seva_type, "specific_print_format"
    )
    template = frappe.db.get_value(
        "DJ Receipt Format",
        (
            seva_type_specific_format
            if seva_type_specific_format
            else settings.receipt_format
        ),
        "template",
    )

    return frappe.render_template(template, context={"doc": doc})


def get_pdf_dr(doctype, name, doc=None):
    doc = doc or frappe.get_doc(doctype, name)
    content = get_receipt_content(doc)
    return get_pdf(content)


@frappe.whitelist()
def download_pdf(
    name,
    doctype="Donation Receipt",
    format=None,
    doc=None,
    no_letterhead=0,
    language=None,
    letterhead=None,
):
    if not doc:
        doc = frappe.get_doc("Donation Receipt", name)

    frappe.local.response.filename = get_receipt_filename(doc)
    frappe.local.response.filecontent = get_pdf_dr(doctype, name, doc=None)
    frappe.local.response.type = "pdf"


@frappe.whitelist(allow_guest=True)
def download_pdf_public(
    receiptToken,
    doctype="Donation Receipt",
):
    settings = frappe.get_cached_doc("Dhananjaya Settings")
    key = settings.public_fernet_key.encode()
    f = Fernet(key)
    decryptReceiptId = f.decrypt(receiptToken.encode())
    receiptId = decryptReceiptId.decode()
    doc = frappe.get_doc(doctype, receiptId)
    if doc.docstatus == 2:
        return "This document is cancelled."
    return download_pdf(receiptId, doc)


def get_donor_details(donors):
    if donors is None or len(donors) == 0:
        return {}

    if not isinstance(donors, list):
        donors = [donors]

    donors = list(set(donors))

    donors_string = ",".join([f"'{d}'" for d in donors])

    donor_details = {}

    for i in frappe.db.sql(
        f"""
					select td.name as donor_id,td.full_name as donor_name, td.llp_preacher,
					TRIM(BOTH ',' FROM CONCAT_WS(",",IF(td.pan_no is not null,'✅ PAN',''), IF(td.aadhar_no is not null,'✅ Aadhar',''))) as kyc,
					GROUP_CONCAT(DISTINCT tda.address_line_1,tda.address_line_2,tda.city SEPARATOR' | ') as address,
					GROUP_CONCAT(DISTINCT tdc.contact_no SEPARATOR' , ') as contact,
					td.pan_no,td.aadhar_no
					from `tabDonor` td
					left join `tabDonor Contact` tdc on tdc.parent = td.name
					left join `tabDonor Address` tda on tda.parent = td.name
					where 1
					and td.name IN ({donors_string})
					group by td.name
					""",
        as_dict=1,
    ):
        donor_details.setdefault(i["donor_id"], i)

    donation_details = {}
    if len(donor_details.keys()) > 0:
        for i in frappe.db.sql(
            f"""
						select tdr.donor, count(*) as times, sum(tdr.amount) as total_donation, MAX(tdr.receipt_date) as last_donation,
						IF(MAX(tdr.receipt_date) > NOW() - INTERVAL 2 year,"active","non_active") as status
						from `tabDonation Receipt` tdr
						where tdr.workflow_state = 'Realized' and tdr.donor IN ({",".join([f"'{name}'" for name in donor_details.keys()])})
						group by donor
						""",
            as_dict=1,
        ):
            donation_details.setdefault(i["donor"], i)
    for d in donor_details:
        donation = {"times": 0, "total_donation": 0, "last_donation": None}
        if d in donation_details:
            donation = donation_details[d]
        donor_details[d].update(donation)

    return donor_details


@frappe.whitelist()
def get_best_contact_address(docname):
    try:
        donor_doc = frappe.get_doc("Donor", docname)
    except:
        return None, None, None
    address = None
    for add in donor_doc.addresses:
        if add.preferred:
            address = add
    if address is None and len(donor_doc.addresses) > 0:
        address = donor_doc.addresses[0]

    contact = None
    for ct in donor_doc.contacts:
        cleaned_ct = re.sub("[^0-9+ -]", "", ct.contact_no)
        if len(cleaned_ct) >= 10:
            contact = cleaned_ct
            break
    if contact is None and len(donor_doc.contacts) > 0:
        contact = donor_doc.contacts[0].contact_no

    email = None
    if len(donor_doc.emails) > 0:
        email = donor_doc.emails[0].email

    return get_formatted_address(address), contact, email


def get_formatted_address(address):
    if address is None:
        return ""
    else:
        values = [
            address.address_line_1,
            address.address_line_2,
            address.city,
            address.state,
            address.pin_code,
        ]
        non_null_values = [
            i.strip(",") for i in values if (i is not None and len(i) > 0)
        ]
        return ", ".join(non_null_values)


def get_donation_companies():
    settings = frappe.get_doc("Dhananjaya Settings")
    companies = []
    for c in settings.company_details:
        companies.append(c.company)
    return companies


def get_credits_equivalent(company: str, credits: float):
    settings = frappe.get_cached_doc("Dhananjaya Settings")
    for s in settings.company_details:
        if s.company == company:
            return credits * s.credit_value
    return credits


def get_credit_values():
    settings = frappe.get_cached_doc("Dhananjaya Settings")
    values = {}
    for s in settings.company_details:
        values.setdefault(s.company, s.credit_value)
    return values


def is_null_or_blank(value):
    """
    Check if a string is either None, empty, or consists only of whitespace characters.

    Args:
        value (str): The string to check.

    Returns:
        bool: True if the string is None, empty, or blank; otherwise, False.
    """
    return value is None or (isinstance(value, str) and value.strip() == "")


def sanitise_str(val: str):
    return re.sub(r"\s+", " ", val).strip()


def send_receipt_in_mail():
    receipt_pdf = get_pdf_dr("Donation Receipt", "HKMJ-DR2401-0030", doc=None)
    frappe.sendmail(
        recipients=["nrhdasa@gmail.com"],
        attachments=[receipt_pdf],
        subject="Receipt Demo",
        message="<p>Demo Receipt</p>",
    )


def is_donor_kyc_available(donor_id):
    pan, aadhar = frappe.db.get_value("Donor", donor_id, ["pan_no", "aadhar_no"])
    if pan or aadhar:
        return True
    return False


def is_donor_request_kyc_available(donor_request_id):
    pan, aadhar = frappe.db.get_value(
        "Donor Creation Request", donor_request_id, ["pan_number", "aadhar_number"]
    )
    if pan or aadhar:
        return True
    return False


## Only for HKCC Reports
# def format_currency(amount):
#     # Convert to string and remove decimals if any
#     amount_str = str(int(amount))

#     # Reverse the string to process from right to left
#     reversed_whole = amount_str[::-1]

#     # Grouping the digits: first group is 3 digits, then groups of 2 digits
#     grouped_digits = [reversed_whole[:3]] + [
#         reversed_whole[i : i + 2] for i in range(3, len(reversed_whole), 2)
#     ]

#     # Reverse back the groups and join them with commas
#     indian_formatted = ",".join(grouped_digits)[::-1]

#     return indian_formatted
