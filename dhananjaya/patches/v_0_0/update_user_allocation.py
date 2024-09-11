import frappe
def execute():
    for p in frappe.get_all("LLP Preacher", pluck ='name'):
        prch_doc = frappe.get_doc("LLP Preacher",p)
        if prch_doc.erp_user:
            prch_doc.append('allowed_users',{'user' : prch_doc.erp_user})
        prch_doc.save()
    