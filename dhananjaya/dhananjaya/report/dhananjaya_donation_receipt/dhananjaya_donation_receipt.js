// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Dhananjaya Donation Receipt"] = {
  filters: [
    {
      fieldname: "company",
      label: __("Company"),
      fieldtype: "Link",
      options: "Company",
      width: 100,
    },
    {
      fieldname: "preacher",
      label: __("Preacher"),
      fieldtype: "Link",
      options: "LLP Preacher",
      width: 80,
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
      fieldname: "donor",
      label: __("Donor"),
      fieldtype: "Link",
      options: "Donor",
      width: 120,
    },
    {
      fieldname: "seva_type",
      label: __("Seva Type"),
      fieldtype: "Link",
      options: "Seva Type",
      width: 80,
    },
    {
      fieldname: "seva_subtype",
      label: __("Seva Subtype"),
      fieldtype: "Link",
      options: "Seva Subtype",
      width: 80,
    },
    {
      fieldname: "group_by_seva_type",
      label: __("Group by Seva Type"),
      fieldtype: "Check",
      width: 80,
    },
  ],
};
