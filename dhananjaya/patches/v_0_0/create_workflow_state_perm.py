# # Copyright (c) 2022, HKM
# # For license information, please see license.txt

# from __future__ import unicode_literals
# import frappe
# from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
# from frappe.desk.page.setup_wizard.setup_wizard import make_records


# def execute():
#     # records = [
# 	# 	{'doctype': "Custom DocPerm", "role_name": "DCC Preacher"},
# 	# 	{'doctype': "Role", "role_name": "DCC Executive"},
# 	# 	{'doctype': "Role", "role_name": "DCC Manager"},
# 	# 	{'doctype': "Role", "role_name": "DCC Cashier"}
# 	# ]
#     # make_records(records)

# # def execute():
# # 	add_custom_field_in_journal_entry()

# # def add_custom_field_in_journal_entry():
# # 	custom_fields = {
# # 		'Journal Entry':[
# # 			dict(fieldname ='donation_receipt', label ='Donation Receipt',
# # 					fieldtype='Link',options='Donation Receipt',insert_after='bank_account')
# # 		]
# # 	}
# # 	if not frappe.db.exists('Custom Field', {"dt": 'Journal Entry', "fieldname":'for_a_work_order'}):
# # 		create_custom_fields(custom_fields)


