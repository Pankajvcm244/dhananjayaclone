import frappe

def execute():
    # Remove Trailing Commas
    frappe.db.sql("""
                    UPDATE `tabDonor Address`
                    SET address_line_2 = TRIM(TRAILING ',' FROM address_line_2)
                    WHERE address_line_2 LIKE '%,'
                """)
    frappe.db.sql("""
                    UPDATE `tabDonor Address`
                    SET address_line_1 = TRIM(TRAILING ',' FROM address_line_1)
                    WHERE address_line_1 LIKE '%,'
                """)
    # Remove Trailing Space
    frappe.db.sql("""
                    UPDATE `tabDonor Address`
                    SET address_line_2 = TRIM(address_line_2)
                    WHERE address_line_2 LIKE '% '
                """)
    frappe.db.sql("""
                    UPDATE `tabDonor Address`
                    SET address_line_1 = TRIM(address_line_1)
                    WHERE address_line_1 LIKE '% '
                """)
    # Donation Receipt Update Address
    frappe.db.sql("""
                    UPDATE `tabDonation Receipt`
                    SET address = REPLACE(address, ',,', ',')
                    WHERE address LIKE '%,,%';
                """)
    frappe.db.commit()

	