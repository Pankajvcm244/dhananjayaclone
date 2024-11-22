// Copyright (c) 2024, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.query_reports["Dimension-Wise Donation"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default" : frappe.datetime.add_months(frappe.datetime.get_today(), -6),
			"reqd": 1,
			"width" : 80,
		  },
		  {
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"width": 80,
			"default": frappe.datetime.get_today(),
		  },
		  {
			fieldname: "dimension",
			label: __("Select Dimension"),
			fieldtype: "Select",
			default: "Project",
			options: get_accounting_dimension_options(),
			reqd: 1,
		},
		
	]
};
function get_accounting_dimension_options() {
	let options = ["Cost Center", "Project"];
	frappe.db.get_list("Accounting Dimension", { fields: ["document_type"] }).then((res) => {
		res.forEach((dimension) => {
			options.push(dimension.document_type);
		});
	});
	return options;
}