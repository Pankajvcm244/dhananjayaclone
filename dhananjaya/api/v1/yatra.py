import json
import frappe
from dhananjaya.dhananjaya.utils import get_preachers
from frappe.query_builder.functions import Sum
from frappe.query_builder.utils import DocType


@frappe.whitelist()
def get_yatra_details(id):
    yatra = {}

    yatra_details = frappe.get_doc("Seva Subtype", id)
    yatra = {
        "name": yatra_details.name,
        "from_date": yatra_details.from_date,
        "to_date": yatra_details.to_date,
        "seats": get_total_seats(id),
        "status_of_seats": get_seats_status(id),
        "total_bookings": get_total_seats(id) - get_available_seats(id),
        "bookings": get_yatra_bookings(id),
    }
    return yatra


def get_seats_status(seva_subtype):
    yatra_registration = frappe.get_all(
        "Yatra Registration",
        filters={"seva_subtype": seva_subtype, "docstatus": 1},
        pluck="name",
    )
    yatra_registration_str = ", ".join([f"'{name}'" for name in yatra_registration]) or "NULL"

    query = frappe.db.sql(
    f"""
    SELECT 
        rsd.seat_type AS name,
        tyst.seat_type AS seat_type,
        SUM(rsd.count) AS total_booked_seats
    FROM `tabRegistration Seat Detail` rsd
    LEFT JOIN `tabYatra Seat Type` tyst
        ON rsd.seat_type = tyst.name
    WHERE rsd.parent IN ({yatra_registration_str})
    GROUP BY rsd.seat_type
    """,
    as_dict=1,
)

    seats = frappe.get_all(
        "Yatra Seat Detail",
        filters={"parent": seva_subtype},
        fields=["seat_type", "count", "cost"],
    )
    for seat in seats:
        for item in query:
            if item["name"] == seat["seat_type"]:                
                seat["total_booked_seats"] = item["total_booked_seats"] 
                
                break
            
        
    


    return seats


def get_yatra_bookings(seva_subtype):
    preachers = get_preachers()

    bookings = frappe.get_all(
        "Yatra Registration",
        filters={
            "seva_subtype": seva_subtype,
            "docstatus": 1,
            "preacher": ["in", preachers],
        },
        fields=[
            "name",
            "docstatus",
            "seva_subtype",
            "donor",
            "donor_creation_request",
            "donor_name",
            "preacher",
            "total_cost",
        ],
    )
    seat_costs = get_seat_costs(seva_subtype)
    for booking in bookings:
        booking["seats"] = []
        booking["participants"] = []
        booking["total_cost"] =  get_total_payble_amount(seva_subtype, booking.name)
        
        booking_tile = frappe.get_all(
            "Registration Seat Detail",
            filters={"parent": booking.name},
            fields=[
                "seat_type",
                "count",
            ],
        )
        
        booking["participants"]= frappe.get_all(
            "Yatra Participant Details" ,
            filters={"parent": booking.name},
            fields = [
                "travelller_name",
                "gender",
                "age",
                "mobile_number" ,
                "aadhaar_number" ,
            ]
        )
        

        for i in booking_tile:
            seat_total_cost = i.count * seat_costs.get(i.seat_type, 0)
            booking["seats"].append(
                {"seat_type": i.seat_type, "count": i.count, "cost": seat_total_cost}
            )
        booking["total_paid_amount"] = get_total_paid_amount(seva_subtype, booking.name)
    return bookings

def get_seats_map(seva_subtype):
        sevasubtype_doc = frappe.get_doc("Seva Subtype", seva_subtype)
        seats_map = {}
        for s in sevasubtype_doc.seats:
            seats_map[s.seat_type] = frappe._dict(count=s.count, cost=s.cost)
        return seats_map
def get_total_payble_amount(seva_subtype, booking):
    seats_map = get_seats_map(seva_subtype)
    total_amount = 0
    seats =  frappe.get_doc("Yatra Registration", booking).seats
    for rs in seats:
            if rs.seat_type not in seats_map:
                frappe.throw(
                    f"Seat Type : {rs.seat_type} is not available for {seva_subtype}"
                )
            total_amount = total_amount + rs.count * seats_map[rs.seat_type].cost

    return total_amount

@frappe.whitelist()
def get_total_paid_amount(seva_subtype, booking):
    receipt = frappe.get_all(
        "Donation Receipt",
        filters={
            "workflow_state": "Realized",
            "seva_subtype": seva_subtype,
            "yatra_registration": booking,
        },
        pluck="amount",
    )
    total_paid_amount = sum(receipt) if receipt else 0

    return total_paid_amount


@frappe.whitelist()
def get_yatra_tiles():
    page_size = 20
    data = json.loads(frappe.request.data)

    query = frappe.db.sql(
        f"""
    SELECT 
        name,
        from_date,
        to_date,
        creation
    FROM `tabSeva Subtype`
    WHERE `tabSeva Subtype`.is_a_yatra = 1
        AND `tabSeva Subtype`.enabled = 1
    GROUP BY name
    ORDER BY `{data.get("sortfield")}` {data.get("sortOrder")}
    LIMIT {page_size * data.get("Page", 0)}, {page_size}
    """,
        as_dict=1,
    )

    yatra_tiles = {}
    for entry in query:
        if entry.name not in yatra_tiles:
            yatra_tiles.setdefault(
                entry.name,
                {
                    "name": entry.name,
                    "creation": entry.creation,
                    "from_date": entry.from_date,
                    "to_date": entry.to_date,
                    "seats": get_total_seats(entry.name),
                    "costing_details": get_seats_details(entry.name),
                    "total_booked_seats": get_total_seats(entry["name"])
                    - get_available_seats(entry["name"]),
                    "remaining_seats": get_available_seats(entry["name"]),
                },
            )
    data = list(yatra_tiles.values())
    return data


def get_total_seats(seva_subtype):
    seva_subtypes = frappe.get_doc("Seva Subtype", seva_subtype)
    total_seats = 0
    for i in seva_subtypes.seats:
        total_seats += i.count
    return total_seats


def get_seats_details(seva_subtype):
    seats = frappe.get_all(
        "Yatra Seat Detail",
        filters={"parent": seva_subtype},
        fields=["seat_type", "count", "cost"],
    )
    return seats


def get_available_seats(seva_subtype):
    total_seats = get_total_seats(seva_subtype)
    booked_seats = 0
    yatra_registration = frappe.get_all(
        "Yatra Registration",
        filters={"seva_subtype": seva_subtype, "docstatus": 1},
        pluck="name",
    )
    for _ in yatra_registration:
        registration = frappe.get_doc("Yatra Registration", _)

        for j in registration.seats:
            booked_seats += j.count
    return total_seats - booked_seats


def get_seat_costs(seva_subtype):
    cost = {}
    seats = frappe.get_all(
        "Yatra Seat Detail",
        filters={"parent": seva_subtype},
        fields=["seat_type", "cost"],
    )
    for seat in seats:
        cost[seat.seat_type] = seat.cost
    return cost


@frappe.whitelist()
def update_yatra_registration():
    data = json.loads(frappe.request.data)
    yatra_registration =  frappe.get_doc("Yatra Registration", data["name"])
    yatra_registration.participants = []
    yatra_registration.seats = []

    for i in data.get("seats"):
        yatra_registration.append("seats", {"seat_type": i.get("seat_type"), "count": i.get("count")})
    for i in data.get("participants"):
        yatra_registration.append(
            "participants",
            {
                "travelller_name": i.get("travelller_name"),
                "gender": i.get("gender"),
                "age": i.get("age"),
                "mobile_number": i.get("mobile_number"),
                "aadhaar_number": i.get("aadhaar_number"),
            },
        )  
    yatra_registration.save()
    yatra_registration = frappe.get_doc("Yatra Registration", data["name"])
    seats_map = get_seats_map(yatra_registration.seva_subtype)  
    total_amount = 0
    seats =  yatra_registration.seats
    for rs in seats:
            if rs.seat_type not in seats_map:
                frappe.throw(
                    f"Seat Type : {rs.seat_type} is not available for {yatra_registration.seva_subtype}"
                )
            total_amount = total_amount + rs.count * seats_map[rs.seat_type].cost

    yatra_registration.total_cost = total_amount 
    yatra_registration.flags.ignore_submit = True
    yatra_registration.flags.ignore_validate_update_after_submit = True
    yatra_registration.save() 
