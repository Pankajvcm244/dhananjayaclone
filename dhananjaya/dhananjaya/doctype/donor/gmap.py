from dhananjaya.dhananjaya.utils import get_preachers
import frappe

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