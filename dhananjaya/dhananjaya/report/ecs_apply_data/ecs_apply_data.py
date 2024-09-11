# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

from dhananjaya.dhananjaya.doctype.donor.ecs_utils import get_ecs_months
import frappe
from frappe.utils.data import getdate


def execute(filters=None):
	
	apply_date = getdate(filters.apply_date)

	donors = frappe.get_all("Donor",filters = {'ecs_active':1,'ecs_bank':filters.get('ecs_bank')}, fields = ['name','ecs_id','ecs_amount','opening_date','periodicity','settlement_day','closing_date'], order_by=' FIELD(settlement_day, 7, 14, 21)')
	
	data = [ ['Unique_Registration_Number', 'Amount', 'Bill_Due_Date', 'Actual_Bill_Due_Date', ''] ]

	

	for d in donors:
		months = list((get_ecs_months(d['opening_date'], d['periodicity'])).keys())
		if apply_date.month in months:
			due_date = apply_date.replace(day = int(d['settlement_day']))
			if due_date <= getdate(d['closing_date']):
				due_date = due_date.strftime("%d-%b-%y")
				data.append([ d['ecs_id'], d['ecs_amount'], due_date, due_date, ''])
	columns = [
		{
			'label' : 'Unique Reference Number',
			'fieldtype' : 'Data',
			'width' : 200,
		},
		{
			'label' : 'Debit Amount',
			'fieldtype' : 'Data',
			'width' : 200,
		},
		{
			'label' : 'Debit Date',
			'fieldtype' : 'Data',
			'width' : 200,
		},
		{
			'label' : 'Actual Bill or debit date',
			'fieldtype' : 'Data',
			'width' : 200,
		},
		{
			'label' : 'Remarks',
			'fieldtype' : 'Data',
			'width' : 200,
		}
	]

	# columns, data = [], []
	return columns, data
