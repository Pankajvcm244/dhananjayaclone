import frappe


@frappe.whitelist()
def get_yatra_details(id):
    yatra_details = frappe.get_doc("Seva Subtype", id).as_dict()

    yatra_details.setdefault(
        "bookings",
        frappe.db.get_list(
            "Yatra Registration",
            fields=["*"],
            filters={"seva_subtype": id, "docstatus": 1},
            order_by="creation desc",
        ),
    )

    return yatra_details
