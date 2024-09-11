import re
import frappe
from rapidfuzz import fuzz


def identify_donor(full_name_received, contact, email, pan, aadhar):
    donor = None
    if pan:
        pan_donors = frappe.db.sql(
            f"""
                select name
                from `tabDonor`
                where REGEXP_REPLACE(pan_no, '\\s+', '') = '{pan}'
                """,
            as_dict=1,
        )
        if len(pan_donors) == 1:
            return pan_donors[0]["name"]
        elif len(pan_donors) > 1:
            similar_donors = [p["name"] for p in pan_donors]
            donor = fuzzy_match_donor_name(full_name_received, similar_donors)

    if (donor is None) and aadhar:
        aadhar_donors = frappe.db.sql(
            f"""
                select name
                from `tabDonor`
                where REGEXP_REPLACE(aadhar_no, '\\s+', '') = '{aadhar}'
                """,
            as_dict=1,
        )
        if len(aadhar_donors) == 1:
            return aadhar_donors[0]["name"]
        elif len(aadhar_donors) > 1:
            similar_donors = [a["name"] for a in aadhar_donors]
            donor = fuzzy_match_donor_name(full_name_received, similar_donors)

    if (donor is None) and contact:
        contact = re.sub(r"\D", "", contact)[-10:]
        contacts = frappe.db.sql(
            f"""
                select contact_no,parent
                from `tabDonor Contact`
                where REGEXP_REPLACE(contact_no, '[^0-9]+', '') LIKE '%{contact}%' and parenttype = 'Donor'
                """,
            as_dict=1,
        )
        if len(contacts) > 0:
            similar_donors = [c["parent"] for c in contacts]
            donor = fuzzy_match_donor_name(full_name_received, similar_donors)

    # if (donor is None) and email:
    #     emails = frappe.db.sql(
    #         f"""
    #             select email,parent
    #             from `tabDonor Email`
    #             where REGEXP_REPLACE(email, '\s+', '') LIKE '%{email}%' and parenttype = 'Donor'
    #             """,
    #         as_dict=1,
    #     )
    #     if len(emails) > 0:
    #         donor = emails[0]["parent"]
    return donor


def identify_patron(contact, email, pan, aadhar):
    patron = None
    if pan:
        pan_patrons = frappe.db.sql(
            f"""
                select name
                from `tabPatron`
                where REGEXP_REPLACE(pan_no, '\\s+', '') = '{pan}'
                """,
            as_dict=1,
        )
        if len(pan_patrons) > 0:
            patron = pan_patrons[0]["name"]

    if (patron is None) and aadhar:
        aadhar_patrons = frappe.db.sql(
            f"""
                select name
                from `tabPatron`
                where REGEXP_REPLACE(aadhar_no, '\\s+', '') = '{aadhar}'
                """,
            as_dict=1,
        )
        if len(aadhar_patrons) > 0:
            patron = aadhar_patrons[0]["name"]

    if (patron is None) and contact:
        contacts = frappe.db.sql(
            f"""
                select contact_no,parent
                from `tabDonor Contact`
                where 
                    REGEXP_REPLACE(contact_no, '[^0-9]+', '') LIKE '%{contact}%' 
                    and parenttype = 'Patron'
                """,
            as_dict=1,
        )
        if len(contacts) > 0:
            patron = contacts[0]["parent"]

    # if (donor is None) and email:
    #     emails = frappe.db.sql(
    #         f"""
    #             select email,parent
    #             from `tabDonor Email`
    #             where REGEXP_REPLACE(email, '\s+', '') LIKE '%{email}%' and parenttype = 'Donor'
    #             """,
    #         as_dict=1,
    #     )
    #     if len(emails) > 0:
    #         donor = emails[0]["parent"]
    return patron


def fuzzy_match_donor_name(full_name_received, similar_donors):
    fuzzy_token_ratios = {}
    for d in similar_donors:
        donor_name = frappe.db.get_value("Donor", d, "full_name")
        fuzzy_token_ratios[d] = fuzz.token_set_ratio(donor_name, full_name_received)

    max_key = max(fuzzy_token_ratios, key=fuzzy_token_ratios.get)
    max_ratio = fuzzy_token_ratios[max_key]

    if max_ratio > 70:
        return max_key

    return None
