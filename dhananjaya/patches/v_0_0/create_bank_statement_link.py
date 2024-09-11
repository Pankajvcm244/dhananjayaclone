from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    custom_fields = {
        'Journal Entry':[
            dict(fieldname ='donation_receipt', label ='Donation Receipt',
					fieldtype='Link',options='Donation Receipt', insert_after= "tax_withholding_category"),
            dict(fieldname ='bank_statement_name', label ='Bank Statement Name',
					fieldtype='Data',insert_after='donation_receipt',hidden = 1, read_only = 1 )
        ]}
    create_custom_fields(custom_fields)

	