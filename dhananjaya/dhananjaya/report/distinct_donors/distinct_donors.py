# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

from datetime import datetime
import re
import frappe


def execute(filters=None):
    filters.company = frappe.parse_json(filters.get("company"))

    contacts_map = get_contacts_map()
    donors_map = get_donors_map()

    def get_similar_donors(mobile, linked_mobiles, linked_donors):
        if mobile in linked_mobiles:
            return

        linked_mobiles.append(mobile)

        donors = contacts_map[mobile]

        for d in donors:
            if d in linked_donors:
                continue

            linked_donors.append(d)

            for child_contact in donors_map[d]:
                get_similar_donors(child_contact, linked_mobiles, linked_donors)

        return linked_mobiles, linked_donors

    mobile_covered = []

    contacts_extended_map = {}

    for key, val in contacts_map.items():
        if key not in mobile_covered:
            linked_contacts, linked_donors = get_similar_donors(key, [], [])
            mobile_covered.extend(linked_contacts)
            contacts_extended_map.setdefault(
                key, dict(contact=key, linked_contacts=",".join(linked_contacts), linked_donors=",".join(linked_donors))
            )

    donor_details = get_donation_details(filters)

    for cem in contacts_extended_map:
        filtered_donors = {
            donor: donor_details[donor]
            for donor in donor_details
            if donor in contacts_extended_map[cem]["linked_donors"]
        }
        donor_names = []
        max_donation_donor = None
        max_donation = 0
        cummulative_donation = 0
        last_donation = datetime.strptime("01-01-2001", "%m-%d-%Y").date()
        first_donation = None
        for fd in filtered_donors:
            donor_names.append(filtered_donors[fd]["full_name"])

            cummulative_donation += filtered_donors[fd]["total_donation"]

            if filtered_donors[fd]["total_donation"] > max_donation:
                max_donation_donor = filtered_donors[fd]
                max_donation = filtered_donors[fd]["total_donation"]

            if filtered_donors[fd]["last_donation"] and last_donation < filtered_donors[fd]["last_donation"]:
                last_donation = filtered_donors[fd]["last_donation"]

            if filtered_donors[fd]["first_donation"]:
                if first_donation is None:
                    first_donation = filtered_donors[fd]["first_donation"]
                elif first_donation < filtered_donors[fd]["first_donation"]:
                    first_donation = filtered_donors[fd]["first_donation"]

        if max_donation_donor is not None:
            main_donor_id = max_donation_donor["donor_id"]
            main_donor_name = max_donation_donor["full_name"]
            main_address = get_donor_address(max_donation_donor["donor_id"])
            main_donor_preacher = max_donation_donor["llp_preacher"]
        else:
            main_donor_id = None
            main_donor_name = ""
            main_address = ""
            main_donor_preacher = ""

        contacts_extended_map[cem].update(
            dict(
                linked_names=",".join(donor_names),
                cummulative_donation=cummulative_donation,
                main_donor_id=main_donor_id,
                main_donor_name=main_donor_name,
                main_address=main_address,
                main_donor_preacher=main_donor_preacher,
                last_donation=last_donation,
                first_donation=first_donation,
            )
        )

    columns = get_columns()
    data = list(contacts_extended_map.values())

    # columns, data = [], []
    return columns, data


def get_contacts_map():
    contacts = frappe.get_all("Donor Contact", fields=["*"], filters={"parent": ["!=", ""], "parenttype": "Donor"})
    contacts_map = {}

    for i, c in enumerate(contacts):
        sanitised_mobile = sanitize_mobile_number(c["contact_no"])

        if is_a_valid_number(sanitised_mobile):
            ## Contacts Mapping
            if sanitised_mobile not in contacts_map:
                contacts_map.setdefault(sanitised_mobile, [c["parent"]])
            else:
                contacts_map[sanitised_mobile].append(c["parent"])

    return contacts_map


def get_donors_map():
    donors_map = {}
    for dc in frappe.db.sql(
        """
                    select td.name as donor,tdc.contact_no as contact
                    from `tabDonor` td
                    join `tabDonor Contact` tdc
                    on td.name = tdc.parent
                    """,
        as_dict=1,
    ):
        sanitised_mobile = sanitize_mobile_number(dc["contact"])

        if is_a_valid_number(sanitised_mobile):
            if dc["donor"] not in donors_map:
                donors_map.setdefault(dc["donor"], [sanitised_mobile])
            else:
                donors_map[dc["donor"]].append(sanitised_mobile)
    return donors_map


def get_donor_address(donor):
    d = frappe.db.sql(
        f"""
                select GROUP_CONCAT(
                        DISTINCT 
                        tda.address_line_1,
                        IF(COALESCE(TRIM(tda.address_line_2), "") = "","",CONCAT(", ",tda.address_line_2)),
                        IF(COALESCE(TRIM(tda.city), "") = "","",CONCAT(", ",tda.city)),
                        IF(COALESCE(TRIM(tda.state), "") = "","",CONCAT(", ",tda.state)),
                        IF(COALESCE(TRIM(tda.pin_code), "") = "","",CONCAT(" - ",tda.pin_code))
                        SEPARATOR' | ') as address
                from `tabDonor` td
                left join `tabDonor Address` tda on tda.parent = td.name
                where td.name = '{donor}'
                group by td.name
                    """,
        as_dict=1,
    )
    if len(d) == 0:
        return "No Address"
    return d[0]["address"]


def get_donation_details(filters):
    donor_details_map = {}
    companies_string = ",".join(["'" + c + "'" for c in filters.company])
    for d in frappe.db.sql(
        f""" select 
                            td.name as donor_id, td.full_name, td.llp_preacher,
                            count(*) as times,
                            sum(tdr.amount) as total_donation,
                            min(tdr.receipt_date) as first_donation,
                            max(tdr.receipt_date) as last_donation
						from `tabDonation Receipt` tdr
                        join `tabDonor` td on td.name = tdr.donor
						where tdr.docstatus = 1
                        and tdr.receipt_date >= '{filters.get("from_date")}'
                        and tdr.company in ({companies_string})
						group by td.name
                    """,
        as_dict=1,
    ):
        donor_details_map.setdefault(d["donor_id"], d)
    return donor_details_map


def is_a_valid_number(contact_no):
    if re.match(r"^\d{10}$", contact_no):
        return True
    else:
        return False


def sanitize_mobile_number(mobile_string):
    # Remove all spaces from the mobile number string
    mobile_string = mobile_string.replace(" ", "")

    # Remove the optional "+91" prefix if it exists
    mobile_string = re.sub(r"^\+91", "", mobile_string)

    # Remove any non-digit characters from the string
    mobile_string = re.sub(r"\D", "", mobile_string)

    # Replace the specific character "0141" with an empty string
    mobile_string = mobile_string.replace("0141", "")

    # Remove leading zeros from the beginning of the string
    mobile_string = mobile_string.lstrip("0")

    return mobile_string


def get_columns():
    columns = [
        {
            "fieldname": "contact",
            "label": "Contact Number",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "fieldname": "linked_contacts",
            "label": "Linked Contacts",
            "fieldtype": "Data",
            "width": 250,
        },
        {
            "fieldname": "linked_donors",
            "label": "Linked Donors",
            "fieldtype": "Data",
            "width": 250,
        },
        {
            "fieldname": "linked_names",
            "label": "Linked Names",
            "fieldtype": "Data",
            "width": 250,
        },
        {
            "fieldname": "cummulative_donation",
            "label": "Cummulative Donation",
            "fieldtype": "Currency",
            "width": 250,
        },
        {
            "fieldname": "first_donation",
            "label": "First Donation",
            "fieldtype": "Date",
            "width": 100,
        },
        {
            "fieldname": "last_donation",
            "label": "Last Donation",
            "fieldtype": "Date",
            "width": 100,
        },
        {
            "fieldname": "main_donor_id",
            "label": "Main Donor",
            "fieldtype": "Link",
            "options": "Donor",
            "width": 100,
        },
        {
            "fieldname": "main_donor_name",
            "label": "Main Donor Name",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "fieldname": "main_donor_preacher",
            "label": "Preacher",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "fieldname": "main_address",
            "label": "Main Donor Address",
            "fieldtype": "Data",
            "width": 300,
        },
    ]
    return columns
