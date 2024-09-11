import frappe


@frappe.whitelist()
def get_patrons_total_commitment():
    return {
        "value": frappe.db.sql("""SELECT SUM( committed_amount ) FROM `tabPatron` """)[
            0
        ][0],
        "fieldtype": "Currency",
    }


@frappe.whitelist()
def get_patrons_total_completed():
    return {
        "value": frappe.db.sql("""SELECT SUM( total_donated ) FROM `tabPatron` """)[0][
            0
        ],
        "fieldtype": "Currency",
    }


@frappe.whitelist()
def get_active_preachers():
    return {
        "value": frappe.db.sql(
            """
                               SELECT count(DISTINCT llp.name) 
                               FROM `tabLLP Preacher` llp 
                               JOIN `tabDonation Receipt` tdr 
                               ON llp.name = tdr.preacher
                               WHERE tdr.receipt_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
                               """
        )[0][0],
        "fieldtype": "Int",
    }


# {
# 	"value": value,
# 	"fieldtype": "Currency",
# 	"route_options": {"from_date": "2023-05-23"},
# 	"route": ["query-report", "Permitted Documents For User"]
# }
