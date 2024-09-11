// Copyright (c) 2024, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.query_reports["Gifts Eligibility"] = {
	"filters": [
		{
			"fieldname": "gift",
			"label": __("Gift"),
			"fieldtype": "MultiSelectList",
			"options": "Patron Gift",
			get_data: function (txt) {
				return frappe.db.get_link_options('Patron Gift', txt, {});
			}
		},
		{
			"fieldname": "card",
			"label": __("Card"),
			"fieldtype": "MultiSelectList",
			"options": "Patron Card Type",
			get_data: function (txt) {
				return frappe.db.get_link_options('Patron Card Type', txt, {});
			}
		},
		// {
		// 	fieldname: "preacher",
		// 	label: __("Preacher"),
		// 	fieldtype: "Link",
		// 	options: "LLP Preacher",
		// 	width: 80,
		// },
		// {
		// 	fieldname: "patron",
		// 	label: __("Patron"),
		// 	fieldtype: "Link",
		// 	options: "Patron",
		// 	width: 80,
		// },
		// {
		// 	fieldname: "gift",
		// 	label: __("Gift"),
		// 	fieldtype: "Link",
		// 	options: "Patron Gift",
		// 	width: 80,
		// },

		// {
		// 	fieldname: "patron_seva_type",
		// 	label: __("Patron Level"),
		// 	fieldtype: "Link",
		// 	options: "Patron Seva Type",
		// 	width: 80,
		// },
	]
};
