import frappe
import re
from frappe.utils import validate_email_address
import dhananjaya.dhananjaya.doctype.dhananjaya_import_settings.constant_maps as maps
from dhananjaya.dhananjaya.doctype.dhananjaya_import_settings.utils import run_query


@frappe.whitelist()
def import_preachers(*args, **kwargs):
    data = run_query(
        """select PREACHER_CODE
						from view_receipt_details vrd 
						union 
						select PREACHER_CODE  
						from view_donor_details"""
    )
    for d in data:
        preacher = frappe.get_doc(
            doctype="LLP Preacher",
            initial=d["PREACHER_CODE"],
            full_name=d["PREACHER_CODE"],
        )
        preacher.insert(ignore_if_duplicate=True)


@frappe.whitelist()
def import_countries(*args, **kwargs):
    data = run_query("SELECT DISTINCT RES_COUNTRY from `view_donor_details`")
    for d in data:
        if d["RES_COUNTRY"] is not None and d["RES_COUNTRY"].strip() != "":
            country = frappe.get_doc(doctype="Country", country_name=d["RES_COUNTRY"])
            country.insert(ignore_if_duplicate=True)
    data = run_query("SELECT DISTINCT OFF_COUNTRY from `view_donor_details`")
    for d in data:
        if d["OFF_COUNTRY"] is not None and d["OFF_COUNTRY"].strip() != "":
            country = frappe.get_doc(doctype="Country", country_name=d["OFF_COUNTRY"])
            country.insert(ignore_if_duplicate=True)
    data = run_query("SELECT DISTINCT OTHER_COUNTRY from `view_donor_details`")
    for d in data:
        if d["OTHER_COUNTRY"] is not None and d["OTHER_COUNTRY"].strip() != "":
            country = frappe.get_doc(doctype="Country", country_name=d["OTHER_COUNTRY"])
            country.insert(ignore_if_duplicate=True)


@frappe.whitelist()
def import_salutations(*args, **kwargs):
    # Initially, we will just fetch them. Later in ERP, we will merge and refactor them.
    data = run_query("SELECT DISTINCT SALUTATION from `view_donor_details`")
    for d in data:
        if d["SALUTATION"] is not None and d["SALUTATION"].strip() != "":
            salutation = frappe.get_doc(
                doctype="Salutation", salutation=d["SALUTATION"]
            )
            salutation.insert(ignore_if_duplicate=True)


@frappe.whitelist()
def import_donors(*args, **kwargs):
    settings = frappe.get_cached_doc("Dhananjaya Import Settings")
    test_string = f" limit {settings.test_run_records}" if settings.is_a_test else ""
    companies = ",".join([str(c.old_trust_code) for c in settings.companies_to_import])
    data = run_query(
        f"SELECT * from `view_donor_details` WHERE TRUST_ID IN ({companies}) {test_string}"
    )
    ind = 0
    for ind, d in enumerate(data):
        frappe.enqueue(
            insert_a_donor,
            queue="short",
            job_name="Inserting Donor",
            timeout=100000,
            d=d,
        )
        ind += 1


def insert_a_donor(d):
    doc = frappe.new_doc("Donor")
    doc.old_donor_id = d["DONOR_ID"]
    doc.old_trust_code = d["TRUST_ID"]
    doc.salutation = d["SALUTATION"]
    doc.first_name = d["FIRST_NAME"]
    doc.last_name = d["LAST_NAME"]
    doc.spouse_name = d["SPOUSE_NAME"]
    if d["DATE_OF_BIRTH"]:
        doc.date_of_birth = d["DATE_OF_BIRTH"]
    doc.llp_preacher = d["PREACHER_CODE"]

    contact_nos = []
    emails = []

    mail_pref = None
    if d["MAILING_PREF"] in ["O", "R"]:
        mail_pref = "RES" if d["MAILING_PREF"] == "R" else "OFF"
    for atype in maps.ADDRESS_TYPES:
        if d[f"{atype}_ADDR_LINE_1"] is not None and d[f"{atype}_ADDR_LINE_1"].strip():
            doc.append(
                "addresses",
                {
                    "preferred": 1 if (atype == mail_pref) else 0,
                    "type": maps.ADDRESS_TYPES[f"{atype}"],
                    "address_line_1": clean_str(d[f"{atype}_ADDR_LINE_1"])
                    + clean_str(d[f"{atype}_ADDR_LINE_2"]),
                    "address_line_2": clean_str(d[f"{atype}_ADDR_LINE_3"])
                    + clean_str(d[f"{atype}_ADDR_LINE_4"]),
                    "city": d[f"{atype}_CITY"],
                    "state": get_state(d[f"{atype}_STATE"]),
                    "country": d[f"{atype}_COUNTRY"],
                    "pin_code": (
                        d[f"{atype}_PINCODE"]
                        if (
                            d[f"{atype}_PINCODE"]
                            and is_valid_pin(d[f"{atype}_PINCODE"])
                        )
                        else None
                    ),
                },
            )
        if d[f"{atype}_PHONE"] is not None and d[f"{atype}_PHONE"].strip():
            contact_nos.append(d[f"{atype}_PHONE"])
    contact_nos.append(d["MOBILE_1"])
    contact_nos.append(d["MOBILE_2"])
    contact_nos.append(d["PHONE_1"])
    contact_nos.append(d["PHONE_2"])
    emails.append(validate_email_address(d["EMAIL_1"]))
    emails.append(validate_email_address(d["EMAIL_2"]))
    contact_nos = list(
        set(
            [
                x.replace(" ", "")
                for x in contact_nos
                if (x is not None and x.strip() != "")
            ]
        )
    )
    emails = list(
        set([x.replace(" ", "") for x in emails if (x is not None and x.strip() != "")])
    )

    for contact in contact_nos:
        doc.append("contacts", {"contact_no": contact})
    for email in emails:
        doc.append("emails", {"email": email})
    # fax_data_resolver(d,doc)
    doc.insert()


def clean_str(s):
    if s is None:
        return ""
    return s


def fax_data_resolver(val, doc):
    if val["PAN_NUMBER"] is not None and val["PAN_NUMBER"].strip() != "":
        doc.pan_no = val["PAN_NUMBER"]
    elif re.search("pan", val["FAX_NUMBER"], re.IGNORECASE):
        s = re.sub("[PpAaNn].*[NnOo].*-", "", val["FAX_NUMBER"])
        s = re.sub("[\s\W]", "", s)
        doc.pan_no = s
    elif re.search("AADHAR", val["FAX_NUMBER"], re.IGNORECASE):
        s = re.sub("[AADHARaadhar]\D", "", val["FAX_NUMBER"])
        s = re.sub("[\s\W]", "", s)
        doc.aadhar_no = s
    else:
        doc.unresolved_fax_column = val["FAX_NUMBER"]


def get_state(val):
    if val is None:
        return None
    if val.title() in maps.STATES:
        return val.title()
    return None


def is_valid_pin(pin):
    # Remove any extra spaces
    pin = pin.replace(" ", "")

    if len(pin) != 6:
        return False
    if not pin.isdigit():
        return False
    if int(pin[0]) not in range(1, 10):
        return False
    return True


# Set Patron ID in Donors.
@frappe.whitelist()
def set_patron_in_donors(*args, **kwargs):
    settings = frappe.get_cached_doc("Dhananjaya Import Settings")
    companies = ",".join([str(c.old_trust_code) for c in settings.companies_to_import])
    patrons = run_query(
        f"""SELECT PATRON_ID, group_concat(DONOR_ID) as donors, count(PATRON_ID) as count
						from (
								SELECT DONOR_ID, PATRON_ID
								from view_receipt_details
								where PATRON_ID is not null
								AND TRUST_ID IN ({companies})
								group by DONOR_ID,PATRON_ID ) donor_patron
						group by PATRON_ID"""
    )
    donor_ids = [[int(p["donors"]), p["PATRON_ID"]] for p in patrons if p["count"] == 1]
    defective_count = len([p for p in patrons if p["count"] != 1])
    for donor, patron in donor_ids:
        frappe.db.sql(
            f"""
						update `tabDonor`
						set is_patron=1,old_patron_id='{patron}'
						where old_donor_id = '{donor}'
						"""
        )
    doc = frappe.get_doc("Dhananjaya Import Settings")
    doc.db_set("defective_patrons", defective_count)
    frappe.db.commit()


@frappe.whitelist()
def set_latest_preacher_in_donors(*args, **kwargs):
    donor_preachers = run_query(
        f"""select vrd.DONOR_ID ,vrd.PREACHER_CODE 
									from view_receipt_details vrd 
									join (select DONOR_ID , max(DR_DATE) as date
									from view_receipt_details
									where 1
									group by DONOR_ID) max_r
									on max_r.date = vrd.DR_DATE and max_r.DONOR_ID = vrd.DONOR_ID
									group by vrd.DONOR_ID ,vrd.PREACHER_CODE """
    )
    for r in donor_preachers:
        frappe.db.sql(
            f"""
						update `tabDonor`
						set llp_preacher='{r['PREACHER_CODE']}'
						where old_donor_id = '{r['DONOR_ID']}'
						"""
        )
    frappe.db.commit()


@frappe.whitelist()
def export_defective_patrons(*args, **kwargs):
    from frappe.utils.csvutils import build_csv_response

    patrons = run_query(
        f"""SELECT vrd.PATRON_ID,CONCAT(vpd.FIRST_NAME," ", COALESCE(vpd.LAST_NAME,"")) as patron_name,
								count(DISTINCT vrd.DONOR_ID) as count,
								group_concat(DISTINCT CONCAT(vrd.DONOR_ID," (",vdd.FIRST_NAME," ",COALESCE(vdd.LAST_NAME,""),")") SEPARATOR '|') as donors
							from view_receipt_details vrd
							join view_patron_details vpd
							on vpd.PATRON_ID = vrd.PATRON_ID
							join view_donor_details vdd
							on vdd.DONOR_ID = vrd.DONOR_ID
							where vrd.PATRON_ID is not null
							group by vrd.PATRON_ID
							order by count desc"""
    )
    max_count_row = max(patrons, key=lambda p: p["count"])
    max_count = max_count_row["count"]
    donor_ids = [
        [p["PATRON_ID"], p["patron_name"], p["donors"], p["count"]]
        for p in patrons
        if p["count"] != 1
    ]

    header_row = ["patron", "patron_name", "count"] + [
        f"donor{i}" for i in range(1, max_count)
    ]
    rows = [header_row]
    for patron, patron_name, donors, count in donor_ids:
        donors = donors.split("|")
        donors.extend([" " for i in range(1, max_count - len(donors))])
        rows.append([patron, patron_name, count] + donors)
    build_csv_response(rows, "defective patrons")


@frappe.whitelist()
def download_patron_correction_template(*args, **kwargs):
    from frappe.utils.csvutils import build_csv_response

    header_row = ["donor_id", "patron_id"]
    rows = [header_row]
    rows.append(["12345", "23452"])
    rows.append(["12345", "23452"])
    rows.append(["12345", "23452"])
    build_csv_response(rows, "Patron Correction Template")


@frappe.whitelist()
def upload_patron_correction_template(*args, **kwargs):
    from frappe.utils.csvutils import read_csv_content

    settings = frappe.get_cached_doc("Dhananjaya Import Settings")
    _file = frappe.get_doc(
        "File", {"file_url": settings.patron_correction_template_file}
    )
    fcontent = _file.get_content()
    rows = read_csv_content(fcontent)
    for row in rows[1:]:
        frappe.db.sql(
            f"""
						update `tabDonor`
						set is_patron=1,old_patron_id='{row[1]}'
						where old_donor_id = '{row[0]}'
						"""
        )
    frappe.db.commit()
