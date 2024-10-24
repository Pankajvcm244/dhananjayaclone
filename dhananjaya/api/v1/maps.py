from sympy import limit
import frappe


@frappe.whitelist(allow_guest=True)
def get_countries(query=""):
    return frappe.get_all(
        "API Country",
        filters={"name": ("like", f"%{query}%")},
        pluck="name",
        limit=10,
        order_by="name asc",
    )


@frappe.whitelist(allow_guest=True)
def get_states(country, query=""):
    return frappe.get_all(
        "API State",
        filters={
            "state_name": ("like", f"%{query}%"),
            "country": ("like", f"%{country}%"),
        },
        pluck="state_name",
        limit=50,
        order_by="state_name asc",
    )


@frappe.whitelist(allow_guest=True)
def get_cities(state, query=""):
    return frappe.db.sql(
        f"""
        SELECT city_name
        FROM `tabAPI City`
        JOIN `tabAPI State`
            ON `tabAPI City`.state = `tabAPI State`.name
        WHERE
            city_name LIKE '%{query}%'
            AND state_name LIKE '%{state}%'
        ORDER BY city_name
        LIMIT 50
        """,
        pluck="city_name",
    )
