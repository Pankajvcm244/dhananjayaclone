// Copyright (c) 2024, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.query_reports["Patron Commitment Status"] = {
  filters: [
    {
      fieldname: "level",
      label: __("Patron Level"),
      fieldtype: "Link",
      options: "Patron Seva Type",
      width: 100,
    },
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      width: 100,
      reqd: 1,
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      width: 100,
      reqd: 1,
    },
    {
      fieldname: "include_credits",
      label: __("Include Credits"),
      fieldtype: "Check",
      default: 1,
      width: 100,
    },
    {
      fieldname: "show_all_patrons",
      label: __("Show All Patrons"),
      fieldtype: "Check",
      width: 100,
    },
    {
      fieldname: "summary_option",
      label: __("Report Type"),
      fieldtype: "Select",
      width: 100,
      options: [
        { value: "detailed", label: "Detailed" },
        { value: "summary_month", label: "Summary (By Month)" },
        { value: "summary_narrowed", label: "Summary (Narrowed)" },
      ],
      default: "detailed",
    },
  ],
  formatter: function (value, row, column, data, default_formatter) {
    value = default_formatter(value, row, column, data);
    if (value) {
      if (column && data) {
        if (column.fieldname == "enrolled_date") {
          value = moment(data.enrolled_date).format("DD/MM/YYYY");
        } else if (column.fieldname == "last_donation") {
          value = moment(data.last_donation).format("DD/MM/YYYY");
        }
      }
    }
    return value;
  },
};
