frappe.ui.form.on("Bank Transaction", {
  onload(frm) {
    frm.add_custom_button(__("Create Donation Receipt"), function () {
      frappe.call({
        method:
          "dhananjaya.dhananjaya.statement_utils.get_donation_receipt_from_statement",
        args: {
          statement: frm.doc.name,
        },
        callback: (r) => {
          var doc = frappe.model.sync(r.message);
          frappe.set_route("Form", doc[0].doctype, doc[0].name);
        },
      });
    }, "Actions");
  },
});
