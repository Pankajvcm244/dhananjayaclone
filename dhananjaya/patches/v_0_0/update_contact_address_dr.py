from dhananjaya.dhananjaya.utils import get_best_contact_address
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    receipts = frappe.db.sql(
        """
                    select `tabDonation Receipt`.name, `tabDonation Receipt`.donor
                    from `tabDonation Receipt`
                    join `tabDonor`
                    on `tabDonor`.name = `tabDonation Receipt`.donor
                    where donor is not null and contact is null and `tabDonation Receipt`.docstatus != 2
                        """,
        as_dict=1,
    )

    n = 1000
    chunks = list(divide_chunks(receipts, n))
    for c in chunks:
        c_receipts = c
        for r in c_receipts:
            address, contact, _ = get_best_contact_address(r["donor"])
            frappe.db.set_value("Donation Receipt", r["name"], "contact", contact)
            frappe.db.set_value("Donation Receipt", r["name"], "address", address)
        frappe.db.commit()


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i : i + n]
