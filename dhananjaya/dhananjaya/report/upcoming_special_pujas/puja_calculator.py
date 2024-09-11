import frappe
from datetime import datetime
from dhananjaya.dhananjaya.utils import get_donor_details


def get_puja_dates(from_date, to_date, preachers=[]):
    upcoming_pujas = []
    if not preachers:
        pujas = frappe.db.sql(
            """ select * 
                from `tabSpecial Puja Detail`
                where parentfield = 'puja_details' and parenttype = 'Donor'
            """,
            as_dict=1,
        )
    else:
        preachers = list(set(preachers))
        preachers_string = ",".join([f"'{d}'" for d in preachers])
        pujas = frappe.db.sql(
            f""" select `tabSpecial Puja Detail`.*
                from `tabSpecial Puja Detail`
                join `tabDonor` on `tabSpecial Puja Detail`.parent = `tabDonor`.name
                where parentfield = 'puja_details' and parenttype = 'Donor'
                AND `tabDonor`.llp_preacher IN ({preachers_string})
            """,
            as_dict=1,
        )

    if from_date.year == to_date.year:
        year = from_date.year
        for p in pujas:
            try:
                occasion_date = datetime.strptime(
                    f"{year}-{p['month']}-{p['day']}", "%Y-%B-%d"
                ).date()
                if from_date <= occasion_date <= to_date:
                    upcoming_pujas.append(get_puja_data(p, occasion_date))
            except ValueError as e:
                continue
    else:
        years = list(range(from_date.year, to_date.year + 1, 1))
        for p in pujas:
            for year in years:
                try:
                    occasion_date = datetime.strptime(
                        f"{year}-{p['month']}-{p['day']}", "%Y-%B-%d"
                    ).date()
                    if from_date <= occasion_date <= to_date:
                        upcoming_pujas.append(get_puja_data(p, occasion_date))
                except ValueError as e:
                    continue

    donors = [p["donor"] for p in upcoming_pujas]
    donors_data = get_donor_details(donors)

    for p in upcoming_pujas:
        p.update(donors_data[p["donor"]])

    upcoming_pujas = sorted(upcoming_pujas, key=lambda x: x["date"])

    return upcoming_pujas


def get_puja_data(p, occasion_date):
    data = {
        "date": occasion_date,
        "occasion": p["occasion"],
        "puja_id": p["name"],
        "donor": p["parent"],
        "s_name": p["name"],
    }
    return data
