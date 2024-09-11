// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Donor Search"] = {
  onload: function (reportview) {
    reportview.page.add_inner_button(__("Create Donor"), function () {
      frappe.set_route("Form", "Donor", "new");
    });
  },
  filters: [
    {
      fieldname: "preacher",
      label: __("Preacher"),
      fieldtype: "Link",
      options: "LLP Preacher",
      width: 80,
    },
    {
      fieldname: "full_name",
      label: __("Name"),
      fieldtype: "Data",
      width: 120,
    },
    {
      fieldname: "contact_no",
      label: __("Contact No."),
      fieldtype: "Data",
      width: 80,
    },
    {
      fieldname: "address",
      label: __("Address"),
      fieldtype: "Data",
      width: 80,
    },
    {
      fieldname: "last_donation",
      label: __("Till Last Donation"),
      fieldtype: "Date",
      width: 80,
    },
    {
      fieldname: "records",
      label: __("Records"),
      fieldtype: "Select",
      options: ["50", "100", "500", "1000"],
      default: "50",
      width: 80,
    },
  ],
  formatter: function (value, row, column, data, default_formatter) {
    value = default_formatter(value, row, column, data);
    // console.log(row);
    // console.log(column);

    // if(column.fieldname == 'shortcuts'){
    // 	frappe.route_options = {
    // 		make_new: true,
    // 		doctype: this.frm.doctype,
    // 		donor:
    // 	};
    // 	frappe.set_route("Form/Donation Receipt");
    // }

    if (data["status"] == "active") {
      value = $(`<span>${value}</span>`);
      var $value = $(value).css("color", "green");
      if (column.fieldname == "donor_name") {
        $value = $(value).css("font-weight", "bold");
      }
      value = $value.wrap("<p></p>").parent().html();
    }

    return value;
  },
};
