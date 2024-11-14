import json
import frappe
from dhananjaya.dhananjaya.utils import get_preachers

@frappe.whitelist()
def get_yatra_details(id):
    yatra_details = frappe.get_doc("Seva Subtype", id).as_dict()
    total_booking = frappe.db.sql(
            f"""select ifnull(sum(adult_seats + children_seats),0) from `tabYatra Registration` where seva_subtype = '{id}' and docstatus = 1""",
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

@frappe.whitelist()
def get_yatra_tiles():
    page_size = 20
    data = json.loads(frappe.request.data)
    # print("hare " , data)
    
    query = frappe.db.sql(f"""
        SELECT 
            tss.name,
            tss.from_date,
            tss.to_date,
            tss.seats,
            tss.adult_cost,
            tss.child_cost,
            tss.creation,
            
            IFNULL(SUM(tyr.adult_seats + tyr.children_seats), 0) as total_booked_seats,
            IFNULL(tss.seats - IFNULL(SUM(tyr.adult_seats + tyr.children_seats), 0), tss.seats) as remaining_seats
        FROM `tabSeva Subtype` tss
        LEFT JOIN `tabYatra Registration` tyr
            ON tss.name = tyr.seva_subtype AND tyr.docstatus = 1
        WHERE tss.is_a_yatra = 1
            AND tss.enabled = 1
        GROUP BY tss.name
        ORDER BY 
            tss.{data.get("sortfield")} {data.get("sortOrder")}
        LIMIT {page_size * data.get("Page", 0)}, {page_size}    
            
        """
    ,as_dict=1)



    # print("hare " , query)
    return query