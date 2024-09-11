import frappe
import re
from frappe.utils import validate_email_address, getdate
import dhananjaya.dhananjaya.doctype.dhananjaya_import_settings.constant_maps as maps
from dhananjaya.dhananjaya.doctype.dhananjaya_import_settings.utils import run_query
from datetime import datetime, timedelta
from frappe.model.workflow import apply_workflow

    # data = run_query(
    #     f"""
	# 					SELECT DR_NUMBER, PATRON_ID 
	# 					FROM `view_receipt_details`
	# 					WHERE PATRON_ID IS NOT NULL
	# 					AND (TRUST_ID IN ({companies})) {test_string}"""
    # )

def rectify_patrons():
    from frappe.utils import comma_and
    companies = {}
    settings = frappe.get_cached_doc("Dhananjaya Import Settings")
    for c in settings.companies_to_import:
        companies.setdefault(c.company,c.old_trust_code)
    x = 1
    drs = {}
    old_drs = set()
    for dr in frappe.get_all(
        "Donation Receipt",
        filters = {"patron":["is","set"],"old_dr_no":["is","set"]},
        fields = ["name","old_dr_no","company"]):
        drs.setdefault(f'{companies[dr["company"]]}-{dr["old_dr_no"]}', dr["name"])
        old_drs.add(dr["old_dr_no"])
    
    old_ids_str = ",".join(
        [str(dr) for dr in old_drs]
    )

    data = run_query(f"""
                    select PATRON_ID, TRUST_ID, DR_NUMBER
                    from view_receipt_details
                    where DR_NUMBER IN ({old_ids_str})
                    AND PATRON_ID IS NOT NULL
                    """)
    pts = {}
    for p in frappe.get_all(
        "Patron",
        fields = ["name","old_patron_id","old_trust_code"]):
        pts.setdefault(f'{p["old_trust_code"]}-{p["old_patron_id"]}', p["name"])


    for d in data:
        patronID = d['PATRON_ID']
        if patronID is None:
            receipt_no = drs[f'{d["TRUST_ID"]}-{d["DR_NUMBER"]}']
            frappe.db.set_value("Donation Receipt", receipt_no,'patron',None)
        else:
            receipt_no = drs[f'{d["TRUST_ID"]}-{d["DR_NUMBER"]}']
            ERPPatronID = pts[str(d["TRUST_ID"])+"-"+str(patronID)]
            frappe.db.set_value("Donation Receipt", receipt_no,'patron',ERPPatronID)
    
    frappe.db.commit()
            


@frappe.whitelist()
def import_grade(*args, **kwargs):
    data = run_query("select * from lkp_ptrn_grade")
    for d in data:
        grade = frappe.get_doc(
            enabled=1,
            doctype="Patron Grade",
            grade_name=d["PTRN_GRADE_NAME"],
            pass_type=d["PTRN_PASS_TYPE"],
            sequence=d["PTRN_SEQUENCE"],
            code=d["PTRN_GRADE_CODE"],
        )
        grade.insert(ignore_if_duplicate=True)


@frappe.whitelist()
def import_patron_seva(*args, **kwargs):
    companies = {}
    settings = frappe.get_cached_doc("Dhananjaya Import Settings")
    for c in settings.companies_to_import:
        companies.setdefault(c.old_trust_code, c.company)
    companies_str = ",".join(
        [str(c.old_trust_code) for c in settings.companies_to_import]
    )
    data = run_query(
        f"select * from mstr_ptrn_seva where TRUST_ID IN ({companies_str})"
    )
    for d in data:
        seva = frappe.get_doc(
            enabled=1,
            doctype="Patron Seva Type",
            seva_code=d["SEVA_CODE"],
            seva_name=d["SEVA_NAME"],
            company=companies[d["TRUST_ID"]],
            type=d["SEVA_TYPE"],
            seva_amount=d["SEVA_AMOUNT"],
        )
        seva.insert(ignore_if_duplicate=True)


@frappe.whitelist()
def import_patrons(*args, **kwargs):
    settings = frappe.get_cached_doc("Dhananjaya Import Settings")

    companies_trust_code = {}
    for c in settings.companies_to_import:
        comp_abbr = frappe.db.get_value("Company", c.company, "abbr")
        companies_trust_code.setdefault(
            c.old_trust_code, {"abbr": comp_abbr, "name": c.company}
        )

    test_string = f" limit {settings.test_run_records}" if settings.is_a_test else ""
    companies = ",".join([str(c.old_trust_code) for c in settings.companies_to_import])
    data = run_query(
        f"""SELECT `view_patron_details`.*, `n_ptrn_cards`.CARD_NUMBER, `n_ptrn_cards`.VALID_FROM
						from `view_patron_details`
						left join `n_ptrn_cards`
						on `n_ptrn_cards`.PATRON_ID = `view_patron_details`.PATRON_ID AND `n_ptrn_cards`.CARD_NUMBER IS NOT NULL
						WHERE 1
						AND (`view_patron_details`.TRUST_ID IN ({companies})) {test_string}"""
    )
    # patron_seva_types = frappe.get_all("Patron Seva Type", pluck="name")
    for d in data:
        # patron_seva_types = frappe.get_all("Patron Seva Type", pluck="name")
        doc = frappe.new_doc("Patron")
        doc.salutation = d["SALUTATION"]
        doc.first_name = d["FIRST_NAME"]
        doc.last_name = d["LAST_NAME"]
        doc.llp_preacher = d["CURR_PRCR_CODE"]
        doc.old_patron_id = d["PATRON_ID"]
        doc.old_trust_code = d["TRUST_ID"]
        doc.enrolled_date = d["ENRLD_DATE"]
        doc.committed_amount = d["COMMITED_AMOUNT"]
        doc.seva_type = d["SEVA_CODE"]
        doc.spouse_name = d["SPOUSE_NAME"]
        # if d["CARD_NUMBER"] is not None and d["CARD_NUMBER"].strip():
        #     doc.append(
        #         "cards",
        #         {
        #             "card_type": "Life Patron",
        #             "number": d["CARD_NUMBER"],
        #             "valid_from": d["VALID_FROM"],
        #         },
        #     )
        contact_nos = []
        emails = []

        mail_pref = None
        if d["MAILING_PREF"] in ["O", "R"]:
            mail_pref = "RES" if d["MAILING_PREF"] == "R" else "OFF"
        for atype in maps.ADDRESS_TYPES:
            if (
                d[f"{atype}_ADDR_LINE_1"] is not None
                and d[f"{atype}_ADDR_LINE_1"].strip()
            ):
                doc.append(
                    "addresses",
                    {
                        "preferred": 1 if (atype == mail_pref) else 0,
                        "type": maps.ADDRESS_TYPES[f"{atype}"],
                        "address_line_1": d[f"{atype}_ADDR_LINE_1"]
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
            set(
                [
                    x.replace(" ", "")
                    for x in emails
                    if (x is not None and x.strip() != "")
                ]
            )
        )

        for contact in contact_nos:
            doc.append("contacts", {"contact_no": contact})
        for email in emails:
            doc.append("emails", {"email": email})

        # if doc.seva_type and doc.seva_type not in patron_seva_types:
        #     seva_type_doc = frappe.new_doc("Patron Seva Type")
        #     seva_type_doc.seva_code = doc.seva_type
        #     seva_type_doc.seva_name = doc.seva_type
        #     seva_type_doc.insert()
        #     frappe.db.commit()

        # if not doc.seva_type:
        #     doc.seva_type = "GENERAL"

        doc.insert(ignore_mandatory=True)


def clean_str(s):
    if s is None:
        return ""
    return s


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


# @frappe.whitelist()
def set_patron_in_donations():
    settings = frappe.get_cached_doc("Dhananjaya Import Settings")

    companies_trust_code = {}
    for c in settings.companies_to_import:
        comp_abbr = frappe.db.get_value("Company", c.company, "abbr")
        companies_trust_code.setdefault(
            c.old_trust_code, {"abbr": comp_abbr, "name": c.company}
        )

    test_string = f" limit {settings.test_run_records}" if settings.is_a_test else ""
    companies = ",".join([str(c.old_trust_code) for c in settings.companies_to_import])

    data = run_query(
        f"""
						SELECT DR_NUMBER, PATRON_ID 
						FROM `view_receipt_details`
						WHERE PATRON_ID IS NOT NULL
						AND (TRUST_ID IN ({companies})) {test_string}"""
    )
    old_dr_map = {}
    for r in data:
        old_dr_map.setdefault(str(r["DR_NUMBER"]), r["PATRON_ID"])

    patrons = frappe.db.sql(
        """
                select old_patron_id,name
                from `tabPatron`
                where 1
                """
    )
    patron_map = {str(r[0]): str(r[1]) for r in patrons}

    receipts_map = {}
    for d in frappe.get_all("Donation Receipt", fields=["name", "old_dr_no"]):
        receipts_map.setdefault(d["name"], d["old_dr_no"])
    i = 0
    # print(old_dr_map)
    for key, value in receipts_map.items():
        i = i + 1
        print(f"Task {i}")
        # print(key)
        # print(value)
        value = str(value)
        if value in old_dr_map:
            old_pt_id = old_dr_map[value]
            new_patron = patron_map[str(old_pt_id)]
            frappe.db.set_value("Donation Receipt", key, "patron", new_patron)
            print(f"Updating")
        if i % 1000 == 0:
            frappe.db.commit()
    frappe.db.commit()
    # for ind, d in enumerate(data):
    #     if ind < 1000:
    #         print(f"Working on {ind+1}")
    #         frappe.db.sql(
    #             f"""
    #                         update `tabDonation Receipt`
    #                         join `tabPatron`
    #                         on `tabPatron`.old_patron_id = '{d['PATRON_ID']}' and `tabDonation Receipt`.old_dr_no = '{d['DR_NUMBER']}'
    #                         set patron = `tabPatron`.name
    #                         """
    #         )
    #         if ind % 1000 == 0:
    #             frappe.db.commit()
    # frappe.db.commit()


@frappe.whitelist()
def update_gifts_in_patron(*args, **kwargs):
    for b in ["LP: HINDI", "LP: ENGLISH", "SB: HINDI", "SB: ENGLISH"]:
        doc = frappe.get_doc({"doctype": "Patron Gift", "type": b})
        doc.insert(ignore_if_duplicate=True)
    frappe.db.commit()
    data = frappe.get_all("Patron", fields=["name", "old_patron_id"])
    for d in data:
        query_data = run_query(
            f"""
							SELECT BAHUMANA_DESC, BAHUMANA_DATE
							FROM `view_qbl_bahumanas`
							WHERE PATRON_ID = {d['old_patron_id']}
							AND IS_ISSUED = 'Y'
							AND BAHUMANA_DESC IN ('LP: HINDI', 'LP: ENGLISH', 'SB: HINDI', 'SB: ENGLISH')"""
        )
        for qd in query_data:
            doc = frappe.get_doc("Patron", d["name"])
            doc.append(
                "gifts", {"gift": qd["BAHUMANA_DESC"], "issued_on": qd["BAHUMANA_DATE"]}
            )
            doc.save()
    frappe.db.commit()
