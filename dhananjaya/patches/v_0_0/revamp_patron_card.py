import frappe


def execute():
    for p in frappe.get_all("Patron", fields=["name", "issued_card_no", "patron_card_sr", "card_valid_from"]):
        if p["issued_card_no"] is not None and p["issued_card_no"] != "":
            patron_doc = frappe.get_doc("Patron", p["name"])
            patron_doc.append(
                "cards",
                {
                    "card_type": "Membership",
                    "number": p["issued_card_no"],
                    "serial": p["patron_card_sr"],
                    "valid_from": p["card_valid_from"],
                },
            )
            patron_doc.save()
    frappe.db.commit()
