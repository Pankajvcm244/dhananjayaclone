import frappe
from dhananjaya.dhananjaya.utils import get_credits_equivalent, get_preachers


@frappe.whitelist()
def patron_board():
    preachers = get_preachers()
    preachers_string = ",".join([f"'{p}'" for p in preachers])
    frappe.get_all("Donation Receipt")
    sevas_map = {}
    for seva in frappe.get_all(
        "Patron Seva Type", filters={"enabled": 1}, fields=["name", "seva_amount"], order_by="seva_amount desc"
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
        filters=[["llp_preacher", "in", preachers], ["ashraya_level", "not in", ["null", ""]]],
        fields=["ashraya_level, count(name) as count"],
        group_by="ashraya_level",
    ):
        ashraya_map[i["ashraya_level"]]["count"] = i["count"]
        ashraya_map[i["ashraya_level"]]["level"] = i["ashraya_level"]
    return ashraya_map.values()
