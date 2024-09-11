// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Distinct Donors"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": "Donation From Date",
			"fieldtype": "Date",
			"reqd":1,
			"width":80,
			// "default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"company",
			"label": __("Companies"),
			"fieldtype": "MultiSelectList",
			"reqd":1,
			"options": "Company",
			get_data: function(txt) {
				return frappe.db.get_link_options('Company', txt);
			}
			// get_data: function(txt) {
			// 	return frappe.db.get_link_options('Company', txt, {
			// 		company: frappe.query_report.get_filter_value("company")
			// 	});
			// }
		},
	]
};
