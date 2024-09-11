import frappe


def execute():
    frappe.db.sql(
        """
                    update `tabDonor Creation Request`
                    set llp_preacher = 'DCC'
                    where llp_preacher is null OR llp_preacher = ''
                    """
    )
    frappe.db.commit()
