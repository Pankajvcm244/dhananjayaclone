// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Upcoming Special Pujas"] = {
  filters: [
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      reqd: 1,
      width: 80,
      default: frappe.datetime.get_today(),
      //   frappe.datetime.add_months(frappe.datetime.get_today(),-1), frappe.datetime.get_today
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      reqd: 1,
      width: 80,
      default: frappe.datetime.add_days(frappe.datetime.get_today(), 7),
    },
    {
      fieldname: "preacher",
      label: __("Preacher"),
      fieldtype: "Link",
      options: "LLP Preacher",
      width: 80,
    },
  ],
};
