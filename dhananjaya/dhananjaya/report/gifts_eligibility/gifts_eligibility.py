# Copyright (c) 2024, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns(filters)

    filtered_gifts = frappe.parse_json(filters.get("gift"))

    filtered_cards = frappe.parse_json(filters.get("card"))

    issued_gifts = []
    for issue_gift in frappe.db.sql(
        """
				select tp.name as patron,tpgi.gift
				from `tabPatron` tp
				join `tabPatron Gift Issue` tpgi
				on tp.name = tpgi.parent
				where 1
					"""
    ):
        issued_gifts.append(issue_gift)

    issued_cards = []
    for issue_card in frappe.db.sql(
        """
				select tp.name as patron,tpcd.card_type
				from `tabPatron` tp
				join `tabPatron Card Detail` tpcd
				on tp.name = tpcd.parent
				where 1
					"""
    ):
        issued_cards.append(issue_card)

    eligibles_gifts = []
    if filtered_gifts:
        for eligible_gift in frappe.db.sql(
            f"""
                select tp.name as patron,tp.llp_preacher,tp.full_name,tpg.name as gift
                from `tabPatron` tp
                join `tabPatron Gift` tpg
                on tp.total_donated >= tpg.threshold_amount
                where tpg.name IN ({','.join(["'" + str(item) + "'" for item in filtered_gifts])}) 
                    """,
            as_dict=1,
        ):
            if not (eligible_gift["patron"], eligible_gift["gift"]) in issued_gifts:
                eligibles_gifts.append(eligible_gift)

    eligibles_cards = []
    if filtered_cards:
        seva_type_map = {}
        for st in frappe.get_all("Patron Seva Type", fields=["name", "seva_amount"]):
            seva_type_map.setdefault(st["name"], st["seva_amount"])
        cards = frappe.get_all(
            "Patron Card Type",
            fields=["name", "threshold_amount", "based_seva_type"],
            filters={"name": ["in", filtered_cards]},
        )
        for p in frappe.get_all(
            "Patron",
            fields=[
                "name as patron",
                "seva_type",
                "llp_preacher",
                "full_name",
                "total_donated",
            ],
        ):
            for card in cards:
                if card["based_seva_type"]:
                    if p["total_donated"] >= seva_type_map[p["seva_type"]]:
                        # frappe.errprint("Based Seva")
                        eligibles_cards.append({**p, "gift": card["name"]})
                elif p["total_donated"] >= card["threshold_amount"]:
                    if (p["patron"], card["name"]) not in issued_cards:
                        eligibles_cards.append({**p, "gift": card["name"]})

    data = eligibles_gifts + eligibles_cards

    frappe.errprint(data)

    grouped_data = {}

    for d in data:
        patron_id = d["patron"]
        if patron_id not in grouped_data:
            grouped_data.setdefault(patron_id, d)
        else:
            grouped_data[patron_id]["gift"] = (
                grouped_data[patron_id]["gift"] + ", " + d["gift"]
            )
    final_data = list(grouped_data.values())
    return columns, final_data


def get_columns(filters):
    columns = [
        {
            "fieldname": "patron",
            "label": "Patron ID",
            "fieldtype": "Link",
            "options": "Patron",
            "width": 140,
        },
        {
            "fieldname": "full_name",
            "label": "Patron Name",
            "fieldtype": "Data",
            "options": "Donor",
            "width": 300,
        },
        {
            "fieldname": "llp_preacher",
            "label": "Preacher",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "fieldname": "gift",
            "label": "Gift / Card",
            "fieldtype": "Data",
            "width": 250,
        },
    ]
    return columns
