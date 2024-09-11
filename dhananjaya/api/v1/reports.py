import frappe
from dhananjaya.dhananjaya.utils import get_credits_equivalent, get_preachers
from dhananjaya.dhananjaya.report.donation_cumulative_report.donation_cumulative_report import (
    get_conditions,
)


@frappe.whitelist()
def patron_board():
    preachers = get_preachers()
    preachers_string = ",".join([f"'{p}'" for p in preachers])
    get_credit_values()
    sevas_map = {}
    for seva in frappe.get_all(
        "Patron Seva Type",
        filters={"enabled": 1},
        fields=["name", "seva_amount"],
        order_by="seva_amount desc",
    ):
        patrons_map = {}
        for i in frappe.db.sql(
            f"""
                        select tp.name as patron, SUM(tdr.amount) as completed
                        from `tabDonation Receipt` tdr
                        join `tabPatron` tp on tdr.patron = tp.name
                        where tp.seva_type =  '{seva['name']}'
                        AND tp.llp_preacher IN ({preachers_string})
                        AND tdr.docstatus = 1
                        GROUP BY tp.name
                        """,
            as_dict=1,
        ):
            patrons_map.setdefault(i["patron"], i["completed"])

        for i in frappe.db.sql(
            f"""
                        select tp.name as patron, tdc.company, SUM(tdc.credits) as credits
                        from `tabDonation Credit` tdc
                        join `tabPatron` tp on tdc.patron = tp.name
                        where tp.seva_type =  '{seva['name']}'
                        AND tp.llp_preacher IN ({preachers_string})
                        GROUP BY patron, company
                        """,
            as_dict=1,
        ):
            credits_amount = get_credits_equivalent(i["company"], i["credits"])
            if i["patron"] not in patrons_map:
                patrons_map.setdefault(i["patron"], 0)
            patrons_map[i["patron"]] += credits_amount

        sevas_map.setdefault(
            seva["name"],
            frappe._dict(
                seva=seva["name"],
                seva_amount=seva["seva_amount"],
                enrolled=len(patrons_map),
                commited=len(patrons_map) * seva["seva_amount"],
                completed=sum(patrons_map.values()),
            ),
        )
    return sevas_map.values()


@frappe.whitelist()
def ashraya_board():
    preachers = get_preachers()
    preachers_string = ",".join([f"'{p}'" for p in preachers])
    ashraya_map = {
        "20": frappe._dict(name="Initiated", count=0, level="20"),
        "16": frappe._dict(name="Charanashrya", count=0, level="16"),
        "12": frappe._dict(name="Upasak", count=0, level="12"),
        "8": frappe._dict(name="Sadhak", count=0, level="8"),
        "4": frappe._dict(name="Sevak", count=0, level="4"),
        "1": frappe._dict(name="Sraddhavan", count=0, level="1"),
    }
    for i in frappe.get_all(
        "Donor",
        filters=[
            ["llp_preacher", "in", preachers],
            ["ashraya_level", "not in", ["null", ""]],
        ],
        fields=["ashraya_level, count(name) as count"],
        group_by="ashraya_level",
    ):
        ashraya_map[i["ashraya_level"]]["count"] = i["count"]
        ashraya_map[i["ashraya_level"]]["level"] = i["ashraya_level"]
    return ashraya_map.values()


@frappe.whitelist()
def user_stats(based_on="receipt_date"):
    include_conditions = get_conditions(selective_preachers=True)
    preachers = get_preachers()
    if len(preachers) == 0:
        return {}
    preachers_string = ",".join([f"'{p}'" for p in preachers])
    total_donations = {}
    for i in frappe.db.sql(
        f"""
                    select  company_abbreviation as company, DATE_FORMAT({based_on}, '%b-%y') as month, SUM(amount) as amount
                    from `tabDonation Receipt` dr
                    where {based_on} >= DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 6 MONTH), '%Y-%m-01')
                    and docstatus = 1
                    and dr.preacher IN ({preachers_string})
                    {include_conditions}
                    group by company_abbreviation, DATE_FORMAT({based_on}, '%b-%y')
                    order by company,YEAR({based_on}) asc,MONTH({based_on}) asc   
                    """,
        as_dict=1,
    ):
        key = i["company"] + "|" + i["month"]
        total_donations.setdefault(key, i)
    # Calculate Credits
    for i in frappe.db.sql(
        f"""
                    select  company_abbreviation as company, company as company_full, DATE_FORMAT(posting_date, '%b-%y') as month, SUM(credits) as credits
                    from `tabDonation Credit` dc
                    where posting_date >= DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 6 MONTH), '%Y-%m-01')
                    and dc.preacher IN ({preachers_string})
                    group by company_abbreviation, DATE_FORMAT(posting_date, '%b-%y')
                    order by company,YEAR(posting_date) asc,MONTH(posting_date) asc   
                    """,
        as_dict=1,
    ):
        credits_amount = get_credits_equivalent(i["company_full"], i["credits"])
        key = i["company"] + "|" + i["month"]
        if key not in total_donations:
            total_donations.setdefault(
                key, {"company": i["company"], "month": i["month"], "amount": 0}
            )
        total_donations[key]["amount"] += credits_amount

    return total_donations.values()
