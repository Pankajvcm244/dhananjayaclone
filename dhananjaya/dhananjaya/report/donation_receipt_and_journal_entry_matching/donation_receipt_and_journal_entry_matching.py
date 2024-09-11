# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):

	filters.update({"from_date": filters.get("date_range") and filters.get("date_range")[0], "to_date": filters.get("date_range") and filters.get("date_range")[1]})

	columns = get_columns(filters)
	conditions = get_conditions(filters)


	data = frappe.db.sql("""
					select 
						dr.receipt_date as dr_date,
						je.posting_date as je_date,
						dr.donor as donor,
						dr.name as receipt,
						dr.amount as amount,
						dr.full_name,
						dr.payment_method,
						dr.workflow_state as state,
						je.name as journal_entry,
						je.total_debit as je_amount
					from `tabDonation Receipt` dr
					left join `tabJournal Entry` je
						on je.donation_receipt = dr.name
					where je.docstatus = 1 and dr.docstatus = 1
					%s
					order by dr.receipt_date
					"""%conditions,filters,as_dict=1)
	# columns, data = [], []
	return columns, data

def get_columns(filters):
	columns = [
				{
				"fieldname": "dr_date",
				"label":"DR Date",
				"fieldtype": "Date",
				"width": 100
				},
				{
				"fieldname": "receipt",
				"label":"Donation Receipt",
				"fieldtype": "Link",
				"options":"Donation Receipt",
				"width": 150
				},
				{
				"fieldname": "state",
				"label":"State",
				"fieldtype": "Data",
				"width": 100
				},
				{
				"fieldname": "donor",
				"label":"Donor",
				"fieldtype": "Link",
				"options":"Donor",
				"width": 140
				},
				{
				"fieldname": "full_name",
				"label":"Full Name",
				"fieldtype": "Data",
				"width": 150
				},
				{
				"fieldname": "amount",
				"label":"Amount",
				"fieldtype": "Currency",
				"width": 100
				},
				{
				"fieldname": "payment_method",
				"label":"Method",
				"fieldtype": "Link",
				"options": "DJ Mode of Payment",
				"width": 100
				},
				{
				"fieldname": "journal_entry",
				"label":"Journal Entry",
				"fieldtype": "Link",
				"options": "Journal Entry",
				"width": 100
				},
				{
				"fieldname": "je_amount",
				"label":"JE Amount",
				"fieldtype": "Currency",
				"width": 100
				}
			]
	return columns

def get_conditions(filters):
	from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
	conditions = ""
	
	opts = {
			"company": " and dr.company=%(company)s"
			}
	if filters.get('donor'):
		opts.setdefault('donor',' and dr.donor == %(donor)s')

	if filters.get('payment_method'):
		opts.setdefault('payment_method',' and dr.payment_method = %(payment_method)s')

	if filters.get('date_type') == 'DR Date':
		opts.setdefault('from_date',' and dr.receipt_date >=%(from_date)s')
		opts.setdefault('to_date',' and dr.receipt_date <=%(to_date)s')
	else:
		opts.setdefault('from_date',' and je.receipt_date >=%(from_date)s')
		opts.setdefault('to_date',' and je.receipt_date <=%(to_date)s')

	for key in opts:
		conditions += opts[key]
	
	return conditions
	