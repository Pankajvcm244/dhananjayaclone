import frappe
from datetime import datetime
from dhananjaya.dhananjaya.utils import get_donor_details


def get_patron_puja_dates(from_date, to_date, preachers=[]):
    upcoming_patron_pujas = []
    if not preachers:
        priviledge_pujas = frappe.db.sql(
            """ select * 
                from `tabPatron Privilege Puja`
                where 1
            """,
            as_dict=1,
        )
    else:
        preachers = list(set(preachers))
        preachers_string = ",".join([f"'{d}'" for d in preachers])
        priviledge_pujas = frappe.db.sql(
            f""" select tppp.*
                from `tabPatron Privilege Puja` tppp
                join `tabPatron` tp
                on tppp.patron = tp.name
                AND tp.llp_preacher IN ({preachers_string})
            """,
            as_dict=1,
        )

    if from_date.year == to_date.year:
        year = from_date.year
        for p in priviledge_pujas:
            try:
                occasion_date = datetime.strptime(
                    f"{year}-{p['month']}-{p['day']}", "%Y-%B-%d"
                ).date()
                if from_date <= occasion_date <= to_date:
                    upcoming_patron_pujas.append(get_puja_data(p, occasion_date))
            except ValueError as e:
                continue
    else:
        years = list(range(from_date.year, to_date.year + 1, 1))
        for p in priviledge_pujas:
            for year in years:
                try:
                    occasion_date = datetime.strptime(
                        f"{year}-{p['month']}-{p['day']}", "%Y-%B-%d"
                    ).date()
                    if from_date <= occasion_date <= to_date:
                        upcoming_patron_pujas.append(get_puja_data(p, occasion_date))
                except ValueError as e:
                    continue

    patrons = [p["patron"] for p in upcoming_patron_pujas]
    patrons_data = get_patron_data(patrons)

    for p in upcoming_patron_pujas:
        p.update(patrons_data[p["patron"]])

    upcoming_patron_pujas = sorted(upcoming_patron_pujas, key=lambda x: x["date"])

    return upcoming_patron_pujas


def get_puja_data(p, occasion_date):
    data = {
        "date": occasion_date,
        "occasion": p["occasion"],
        "puja_id": p["name"],
        "patron": p["patron"],
        "patron_name": p["patron_name"],
    }
    return data


def get_patron_data(patrons):
    patrons = list(set(patrons))
    patrons_string = ",".join([f"'{p}'" for p in patrons])
    patron_details = {}
    if len(patrons) > 0:
        for i in frappe.db.sql(
            f"""
                        select td.name as patron_id, td.llp_preacher,
                        GROUP_CONCAT(DISTINCT tda.address_line_1,tda.address_line_2,tda.city SEPARATOR' | ') as address,
                        GROUP_CONCAT(DISTINCT tdc.contact_no SEPARATOR' , ') as contact
                        from `tabPatron` td
                        left join `tabDonor Contact` tdc on tdc.parent = td.name
                        left join `tabDonor Address` tda on tda.parent = td.name
                        where 1
                        and td.name IN ({patrons_string})
                        group by td.name
                        """,
            as_dict=1,
        ):
            patron_details.setdefault(i["patron_id"], i)
    return patron_details
