// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Donation Cumulative Report"] = {
  filters: [
    {
      fieldname: "based_on",
      label: __("Based On"),
      fieldtype: "Select",
      options: ["Realization Date", "Receipt Date"],
      default: "Realization Date",
      width: 100,
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
      fieldname: "only_realized",
      label: __("Only Realized"),
      fieldtype: "Check",
      default: 1,
      width: 80,
    },
  ],
};
