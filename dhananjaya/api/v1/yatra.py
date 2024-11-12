import frappe
from dhananjaya.dhananjaya.utils import get_preachers

@frappe.whitelist()
def get_yatra_details(id):
    yatra_details = frappe.get_doc("Seva Subtype", id).as_dict()
    total_booking = frappe.db.sql(
            f"""select sum(adult_seats + children_seats) from `tabYatra Registration` where seva_subtype = '{id}' and docstatus = 1""",
        )[0][0]
    
    yatra_details.setdefault("total_bookings", total_booking)

    preachers = get_preachers()
    preachers_string = ",".join([f"'{p}'" for p in preachers])

    yatra_details.setdefault("bookings", frappe.db.sql(f"""
        SELECT tyr.*, IFNULL( SUM(tdr.amount), 0) as total_paid_amount
        FROM `tabYatra Registration` tyr
        LEFT JOIN `tabDonation Receipt` tdr
            ON tyr.name = tdr.yatra_registration
        WHERE tyr.preacher IN ({preachers_string})
            AND tyr.seva_subtype = '{id}'
            AND tyr.docstatus = 1
            AND (tdr.name IS NULL OR tdr.workflow_state = 'Realized')
        GROUP BY tyr.name
        ORDER BY creation desc
    """,as_dict=1))

    return yatra_details