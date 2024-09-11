// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["ECS Apply Data"] = {
	"filters": [
		{
			"fieldname": "apply_date",
			"label": __("Applying Date"),
			"fieldtype": "Date",
			"reqd":1,
			"width":80
		},
		{
			"fieldname": "ecs_bank",
			"label": __("Bank"),
			"fieldtype": "Link",
			"options":"Bank",
			"reqd":1,
			"width":80
		},
	]
};
