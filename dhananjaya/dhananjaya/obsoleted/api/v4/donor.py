import json
import re
import frappe
from dhananjaya.dhananjaya.utils import (
    get_preachers,
    get_donor_details,
    is_null_or_blank,
)


@frappe.whitelist()
def members_search(filters, limit_start=None, limit=None):
    filters = json.loads(filters)

    preachers = get_preachers()
    preachers_string = ",".join([f"'{p}'" for p in preachers])

    # join_string = ""
    where_string = ""
    having_string = ""

    ## Preacher Selected
    if not is_null_or_blank(filters.get("preacher_selected")):
        if filters.get("preacher_selected") == "All":
            if frappe.db.get_single_value("Dhananjaya Settings", "hide_others_donors"):
                where_string += f"""  AND td.llp_preacher IN ({preachers_string}) """
        else:
            where_string += (
                f""" AND td.llp_preacher = '{filters.get("preacher_selected")}'"""
            )

    ## Total Donation Amount Selected
    if not is_null_or_blank(filters.get("total_donated_min")):
        if filters.get("total_donated_min"):
            where_string += (
                f"""  AND td.total_donated >= {filters.get("total_donated_min")} """
            )

    if not is_null_or_blank(filters.get("total_donated_max")):
        if filters.get("total_donated_max"):
            where_string += (
                f"""  AND td.total_donated <= {filters.get("total_donated_max")} """
            )

    ## Total Times Donated Selected
    if not is_null_or_blank(filters.get("total_times_donated_min")):
        if filters.get("total_times_donated_min"):
            where_string += f"""  AND td.times_donated >= {filters.get("total_times_donated_min")} """

    ## Last Donation Date Selected
    if not is_null_or_blank(filters.get("last_time_donated_after")):
        where_string += (
            f"""  AND td.last_donation >= '{filters.get("last_time_donated_after")}' """
        )
    if not is_null_or_blank(filters.get("last_time_donated_before")):
        where_string += f"""  AND td.last_donation <= '{filters.get("last_time_donated_before")}' """

    # name, mobile, address, email

    search_field = "name"

    if not is_null_or_blank(filters.get("search_field")):
        search_field = filters.get("search_field")

    query_text = ""

    if not is_null_or_blank(filters.get("text")):
        query_text = filters.get("text")

    if search_field == "name":
        where_string += f""" AND td.full_name LIKE '%{query_text.strip()}%' """
    elif search_field == "mobile":
        query_text = re.sub(r"\D", "", query_text)[-10:]
        having_string += f""" AND contact LIKE '%{query_text}%' """
    elif search_field == "address":
        having_string += f""" AND address LIKE '%{query_text.strip()}%' """
    else:
        frappe.throw("Search Field is not Authorised.")

    limit_string = " LIMIT 100"

    if limit_start:
        limit_string = f" LIMIT {limit_start}, {limit}"

    members = {}

    if not filters.get("member_type"):
        search_doctype = "Donor"
    else:
        if filters.get("member_type") == "donor":
            search_doctype = "Donor"
        elif filters.get("member_type") == "patron":
            search_doctype = "Patron"

    search_doctype_lc = search_doctype.lower()

    ## As Ashraya Level is applicable to only Donor Data

    ashraya_level_select = ""
    if search_doctype == "Donor":
        ashraya_level_select = " td.ashraya_level, "
        if filters.get("ashraya_level") and filters.get("ashraya_level") != "All":
            where_string += (
                f""" AND td.ashraya_level = '{filters.get("ashraya_level")}' """
            )

    ## As Patron Level is applicable to only Patron Data

    patron_level_select = ""
    if search_doctype == "Patron":
        patron_level_select = " td.seva_type, "
        if filters.get("patron_seva_type") and filters.get("patron_seva_type") != "All":
            where_string += (
                f""" AND td.seva_type = '{filters.get("patron_seva_type")}' """
            )
    for i in frappe.db.sql(
        f"""
					select 
                        td.name as {search_doctype_lc}_id,
                        td.full_name as {search_doctype_lc}_name, 
                        td.llp_preacher,
                        {ashraya_level_select} 
                        {patron_level_select}
                        TRIM(BOTH ',' 
                            FROM CONCAT_WS(",",
                                IF(td.pan_no is not null and TRIM(td.pan_no) != '','✅ PAN',''), 
                                IF(td.aadhar_no is not null and TRIM(td.aadhar_no) != '','✅ Aadhar','')
                                )
                            ) as kyc,
					    GROUP_CONCAT(DISTINCT CONCAT(COALESCE(tda.address_line_1,''),', ',COALESCE(tda.address_line_2,''),', ',COALESCE(tda.city,'')) SEPARATOR' |') as address,
					    GROUP_CONCAT(DISTINCT tdc.contact_no SEPARATOR' , ') as contact,
					    td.pan_no,
                        td.aadhar_no,
                        td.last_donation,
                        td.times_donated,
                        td.total_donated
					from `tab{search_doctype}` td
					left join `tabDonor Contact` tdc on tdc.parent = td.name
					left join `tabDonor Address` tda on tda.parent = td.name
					where 1
					{where_string}
					group by td.name
					having 1 {having_string}
					order by FIELD(td.llp_preacher,{preachers_string}) desc
					{limit_string}
					""",
        as_dict=1,
    ):
        members.setdefault(i[f"{search_doctype_lc}_id"], i)

    requested_members = []
    if len(members.keys()) > 0:
        for i in frappe.db.sql(
            f"""
                        select tdc.{search_doctype_lc}
                        from `tabDonor Claim Request` tdc
                        where tdc.status = ""
                        AND tdc.preacher_claimed IN ({preachers_string})
                        AND tdc.{search_doctype_lc} IN ({",".join([f"'{name}'" for name in members.keys()])})
                            """,
            as_dict=1,
        ):
            requested_members.append(i[search_doctype_lc])

    for i in members:
        not_related = False
        requested = False
        if members[i]["llp_preacher"] not in preachers:
            members[i]["contact"] = "***********"
            not_related = True
        if i in requested_members:
            requested = True

        members[i]["not_related"] = not_related
        members[i]["requested"] = requested

    data = list(members.values())

    data.sort(
        key=lambda x: (x["llp_preacher"] in preachers, x["times_donated"]), reverse=True
    )  #

    return data


@frappe.whitelist()
def member_stats(member, type="donor"):
    query_string = """
					select  company_abbreviation as company, SUM(amount) as amount
					from `tabDonation Receipt` dr
					where {}
					and docstatus = 1
					and {} = '{}'
					group by company_abbreviation
					order by company,YEAR(receipt_date) desc,MONTH(receipt_date) desc
					"""
    last_year_query_string = query_string.format(
        " receipt_date > (NOW() - INTERVAL 12 MONTH)", type, member
    )
    total_query_string = query_string.format(" 1 ", type, member)
    return {
        "last_year": frappe.db.sql(last_year_query_string, as_dict=1),
        "total": frappe.db.sql(total_query_string, as_dict=1),
    }


@frappe.whitelist()
def update_donor_contact_address():
    # return frappe.request.data
    data = json.loads(frappe.request.data)
    if data["to_update"] == "Contact":
        frappe.db.set_value(
            "Donor Contact", data["name"], "contact_no", data["contact_no"]
        )
    elif data["to_update"] == "Address":
        ## So that we can directly put full address data as it is in Donor Address
        del data["to_update"]
        if "contact_no" in data:
            del data["contact_no"]
        frappe.db.set_value("Donor Address", data["name"], data)
    return


@frappe.whitelist()
def add_donor_contact_address():
    data = json.loads(frappe.request.data)

    donor = frappe.get_doc("Donor", data["parent"])

    if data["to_add"] == "Contact":
        donor.append(
            "contacts",
            {
                "contact_no": data["contact_no"],
            },
        )
    elif data["to_add"] == "Address":
        del data["to_add"]
        if "contact_no" in data:
            del data["contact_no"]
        donor.append("addresses", data)

    donor.save(ignore_permissions=True)
    return


@frappe.whitelist()
def get_donor_suggestions(filters):
    preachers = get_preachers()
    if len(preachers) == 0:
        return []
    else:
        filters = json.loads(filters)
        page = 0
        if filters.get("page"):
            page = filters.get("page")
        offset = 50
        where_string = ""
        # priority =
        preachers = ", ".join(f"'{p}'" for p in preachers)
        suggestions = {}
        for i in frappe.db.sql(
            f"""
                                        select *
                                        from `tabDonor Suggestion` tds
                                        where tds.disabled != 1 AND preacher IN ({preachers})
                                        {where_string}
                                        ORDER BY priority DESC
                                        limit {page*offset}, {offset}
                                        """,
            as_dict=1,
        ):
            suggestions.setdefault(i["name"], i)

        donor_details = get_donor_details(
            [suggestions[s]["donor"] for s in suggestions]
        )

        for s in suggestions:
            suggestions[s].update(donor_details[suggestions[s]["donor"]])

        data = list(suggestions.values())
        frappe.response.page = page
        return data


@frappe.whitelist()
def last_patron(donorId):
    latest_patron = None

    latest = frappe.db.sql(
        f"""
                    SELECT patron 
                    FROM `tabDonation Receipt`
                    WHERE patron IS NOT NULL
                    AND donor = '{donorId}'
                    ORDER BY receipt_date DESC
                    LIMIT 1;
                    """,
        as_dict=1,
    )

    if len(latest) > 0:
        latest_patron = latest[0]["patron"]
        doc = frappe.get_doc("Patron", latest_patron)
        return {"patron_name": doc.full_name, "patron_id": doc.name}
    return latest_patron


@frappe.whitelist()
def get_donor_lnglats():
    preachers = get_preachers()
    if len(preachers) == 0:
        return []
    preachers_str = ",".join([f"'{p}'" for p in preachers])
    addresses = frappe.db.sql(
        f"""
                select tda.name as address_id,tda.address_line_1,tda.address_line_2,tda.longitude, tda.latitude, td.name as donor_id, td.full_name
                  from `tabDonor Address` tda
                    join `tabDonor` td
                  on td.name = tda.parent
                where td.llp_preacher in ({preachers_str})
                and tda.longitude != 0
                    """,
        as_dict=1,
    )

    return addresses
