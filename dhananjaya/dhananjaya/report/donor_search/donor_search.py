# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.data import get_url


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns(filters)

    # join_string = ""
    where_string = ""
    having_string = ""

    if filters.get("full_name"):
        where_string += f""" AND td.full_name LIKE '%{filters.get("full_name")}%' """

    if filters.get("preacher"):
        where_string += f""" AND td.llp_preacher = '{filters.get("preacher")}' """

    if filters.get("last_donation"):
        # select_string += "group"
        where_string += (
            f""" AND td.last_donation <= '{filters.get("last_donation")}' """
        )
    # else:
    #     where_string += (
    #         f""" AND td.last_donation IS NOT NULL AND td.last_donation != '' """
    #     )
    

    if filters.get("contact_no"):
        # where_string += f" and tdc.contact_no LIKE '%{filters.get("contact_no")}%'"
        having_string += f""" AND contact LIKE '%{filters.get("contact_no")}%' """

    if filters.get("address"):
        # select_string += "group"
        having_string += f""" AND address LIKE '%{filters.get("address")}%' """

    donors = {}
    for i in frappe.db.sql(
        f"""
					select td.name as donor_id,td.full_name as donor_name, td.llp_preacher,
                    td.last_donation,
					TRIM(BOTH ',' 
                        FROM CONCAT_WS(",",
                            IF(td.pan_no is not null and TRIM(td.pan_no) != '','✅ PAN',''), 
                            IF(td.aadhar_no is not null and TRIM(td.aadhar_no) != '','✅ Aadhar','')
                            )
                        ) as kyc,
					GROUP_CONCAT(
                        DISTINCT 
                        tda.address_line_1,
                        IF(COALESCE(TRIM(tda.address_line_2), "") = "","",CONCAT(", ",tda.address_line_2)),
                        IF(COALESCE(TRIM(tda.city), "") = "","",CONCAT(", ",tda.city)),
                        IF(COALESCE(TRIM(tda.state), "") = "","",CONCAT(", ",tda.state)),
                        IF(COALESCE(TRIM(tda.pin_code), "") = "","",CONCAT(" - ",tda.pin_code))
                        SEPARATOR' | ') as address,
					GROUP_CONCAT(DISTINCT tdc.contact_no SEPARATOR' , ') as contact
					from `tabDonor` td
					left join `tabDonor Contact` tdc on tdc.parent = td.name
					left join `tabDonor Address` tda on tda.parent = td.name
					where 1
					{where_string}
					group by td.name
					having 1 {having_string}
                    order by td.last_donation desc
					limit {filters.get("records")}
					""",
        as_dict=1,
    ):
        donors.setdefault(i["donor_id"], i)
    donation_details = {}
    if len(donors.keys()) > 0:
        for i in frappe.db.sql(
            f"""
						select tdr.donor, count(*) as times, sum(tdr.amount) as total_donation,
						IF(MAX(tdr.receipt_date) > NOW() - INTERVAL 2 year,"active","non_active") as status
						from `tabDonation Receipt` tdr
						where tdr.donor IN ({",".join([f"'{name}'" for name in donors.keys()])}) and tdr.docstatus = 1
						group by donor
						""",
            as_dict=1,
        ):
            donation_details.setdefault(i["donor"], i)
    for d in donors:
        donation = {"times": 0, "total_donation": 0}
        if d in donation_details:
            donation = donation_details[d]
        donors[d].update(donation)
        # Shortcuts
        # new_doc = frappe.new_doc("Donation Receipt")
        # new_doc.donor = d
        # shortcuts = f'<a href="{new_doc.get_url()}{new_doc.name}" >MR</a>'
        # shortcuts = f"""
        # 					<a href="#"  onclick = `(function(){{
        # 																				frappe.set_route("Form", "Donation Receipt", {{'Donor': '{d}' }});
        # 																				root.innerHTML = 'This Text is Changed By Inline JavaScript!'
        # 																			}})()`>MR</a>"""
        # # frappe.set_route('query-report', 'Accounts Payable Summary', {company: filters.company})
        # donors[d]['shortcuts'] =shortcuts

    data = list(donors.values())

    data.sort(key=lambda x: x["times"], reverse=True)
    # columns, data = [], []
    return columns, data


def get_columns(filters):
    columns = [
        {
            "fieldname": "donor_id",
            "label": "ID",
            "fieldtype": "Link",
            "options": "Donor",
            "width": 140,
        },
        {
            "fieldname": "llp_preacher",
            "label": "Guide",
            "fieldtype": "Data",
            "width": 60,
        },
        {
            "fieldname": "donor_name",
            "label": "Donor Name",
            "fieldtype": "Data",
            "width": 200,
        },
        # {
        # 	"fieldname": "shortcuts",
        # 	"label": "Shortcuts",
        # 	"fieldtype": "HTML",
        # 	"width": 200,
        # },
        {
            "fieldname": "kyc",
            "label": "KYC",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "fieldname": "contact",
            "label": "Donor Contact",
            "fieldtype": "Data",
            "width": 200,
        },
        {"fieldname": "times", "label": "$$", "fieldtype": "Int", "width": 50},
        {
            "fieldname": "total_donation",
            "label": "Total Donation",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "fieldname": "last_donation",
            "label": "Last Donation",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "fieldname": "address",
            "label": "Donor Address",
            "fieldtype": "Data",
            "width": 1000,
        },
    ]
    return columns
