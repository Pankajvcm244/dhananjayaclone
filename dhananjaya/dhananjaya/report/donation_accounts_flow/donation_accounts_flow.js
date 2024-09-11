// Copyright (c) 2024, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.query_reports["Donation Accounts Flow"] = {
  filters: [
    {
      fieldname: "company",
      label: __("Company"),
      fieldtype: "Link",
      options: "Company",
      width: 100,
      reqd: 1,
    },
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      reqd: 1,
      width: 80,
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      reqd: 1,
      width: 80,
    },
    {
      fieldname: "accounts",
      label: __("Donation Account"),
      fieldtype: "MultiSelectList",
      options: "Account",
      get_data: function (txt) {
        return frappe.db.get_link_options("Account", txt, {
          company: frappe.query_report.get_filter_value("company"),
        });
      },
      reqd: 1,
    },
  ],
};
