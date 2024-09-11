import frappe


def identify_donor(contact, email, pan, aadhar):
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
        if len(pan_donors) > 0:
            donor = pan_donors[0]["name"]

    if (donor is None) and aadhar:
        aadhar_donors = frappe.db.sql(
            f"""
                select name
                from `tabDonor`
                where REGEXP_REPLACE(aadhar_no, '\\s+', '') = '{aadhar}'
                """,
            as_dict=1,
        )
        if len(aadhar_donors) > 0:
            donor = aadhar_donors[0]["name"]

    if (donor is None) and contact:
        contacts = frappe.db.sql(
            f"""
                select contact_no,parent
                from `tabDonor Contact`
                where REGEXP_REPLACE(contact_no, '[^0-9]+', '') LIKE '%{contact}%' and parenttype = 'Donor'
                """,
            as_dict=1,
        )
        if len(contacts) > 0:
            donor = contacts[0]["parent"]

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
