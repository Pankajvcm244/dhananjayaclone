// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Donation Receipt and Journal Entry Matching"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd":1,
			"width":80,
			"default": frappe.defaults.get_user_default("Company")
		},
		// {
		// 	"fieldname": "fiscal_year",
		// 	"label": __("Fiscal Year"),
		// 	"fieldtype": "Link",
		// 	"options": "Fiscal Year",
		// 	"reqd":1,
		// 	"width":80,
		// 	"default": frappe.defaults.get_user_default("Fiscal Year")
		// },
		{
			"fieldname": "date_type",
			"label": __("Date Type"),
			"fieldtype":"Select",
			"options":['DR Date','JE Date'],
			"default":'DR Date',
			"reqd":1
		},
		{
			"fieldname": "date_range",
			"label": __("Date Range"),
			"fieldtype": "DateRange",
			"default": [frappe.datetime.add_months(frappe.datetime.get_today(),-1), frappe.datetime.get_today()],
			"reqd": 1
		},
		{
			"fieldname": "payment_method",
			"label": __("Payment Method"),
			"fieldtype": "Link",
			"options": "DJ Mode of Payment",
			"width":80,
		},
		{
			"fieldname": "donor",
			"label": __("Donor"),
			"fieldtype": "Link",
			"options": "Donor",
			"width":80,
		},
	]
};
