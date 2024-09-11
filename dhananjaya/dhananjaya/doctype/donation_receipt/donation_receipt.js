// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on("Donation Receipt", {
  refresh: function (frm) {
    frm.set_query("asset_item", () => {
      return {
        filters: {
          is_fixed_asset: 1,
          disabled: 0,
        },
      };
    });
    frm.set_query("stock_expense_account", () => {
      return {
        filters: {
          account_type: "Expense Account",
          disabled: 0,
        },
      };
    });
    frm.set_query("payment_gateway_document", () => {
      return {
        filters: {
          company: frm.doc.company,
          receipt_created: 0,
          amount: frm.doc.amount,
        },
      };
    });
    frm.set_query("seva_type", () => {
      return {
        filters: {
          company: frm.doc.company,
          enabled: 1,
        },
      };
    });
    frm.set_query("seva_subtype", () => {
      return {
        filters: {
          enabled: 1,
          is_group: 0,
        },
      };
    });
    frm.set_query("bank_transaction", () => {
      return {
        filters: {
          status: "Unreconciled",
          deposit: frm.doc.amount - frm.doc.additional_charges,
          bank_account: frm.doc.bank_account,
          // date: ['>=',frm.doc.receipt_date]
        },
      };
    });
    frm.set_query("bounce_transaction", () => {
      return {
        filters: {
          status: "Unreconciled",
          withdrawal: frm.doc.amount,
          bank_account: frm.doc.bank_account,
          // date: ['>=',frm.doc.receipt_date]
        },
      };
    });
    frm.set_query("donation_account", () => {
      return {
        filters: {
          company: frm.doc.company,
          is_group: 0,
        },
      };
    });
    frm.set_query("donor", () => {
      return {
        query:
          "dhananjaya.dhananjaya.doctype.donation_receipt.donation_receipt.get_donor",
        filters: {
          // 'account': row.account
        },
      };
    });
    frm.set_query("cash_account", () => {
      return {
        filters: {
          company: frm.doc.company,
          account_type: "Cash",
          is_group: 0,
        },
      };
    });
    frm.set_query("gateway_expense_account", () => {
      return {
        filters: {
          company: frm.doc.company,
          root_type: "Expense",
          is_group: 0,
        },
      };
    });
    frm.add_custom_button(
      __("Create Benefit"),
      function () {
        frappe.call({
          freeze: true,
          method:
            "dhananjaya.dhananjaya.doctype.donation_receipt.operations.get_festival_benefit",
          args: {
            request: frm.doc.name,
          },
          callback: function (r) {
            if (!r.exc) {
              var doc = frappe.model.sync(r.message);
              frappe.set_route("Form", doc[0].doctype, doc[0].name);
            }
          },
        });
      },
      "Operations"
    );
    if (frm.doc.docstatus == 1) {
      frm.add_custom_button(
        __("Cancel"),
        function () {
          frappe.warn(
            "Are you sure you want to proceed?",
            "This action will consequently cancel the Journal Entry and unreconcile the Bank Statement.",
            () => {
              frappe.call({
                freeze: true,
                freeze_message: "Cancelling Linked Documents",
                method:
                  "dhananjaya.dhananjaya.doctype.donation_receipt.operations.receipt_cancel_operations",
                args: {
                  receipt: frm.doc.name,
                },
                callback: function (r) {
                  if (!r.exc) {
                    frappe.msgprint("Successfully Cancelled.");
                  }
                },
              });
            },
            () => {}
          );
        },
        "Operations"
      );
      if (frm.doc.payment_method == "Cash") {
        frm.add_custom_button(
          __("Return Cash"),
          function () {
            frappe.warn(
              "Are you sure you want to proceed?",
              "This action will generate a new Journal Entry to reverse Cash from Cashbook on the given date.",
              () => {
                frappe.prompt(
                  [
                    {
                      label: "Cash Returned Date",
                      fieldname: "returned_date",
                      fieldtype: "Date",
                      required: 1,
                    },
                  ],
                  (values) => {
                    console.log(values.returned_date, values.last_name);
                    frappe.call({
                      freeze: true,
                      freeze_message: "Returning Cash",
                      method:
                        "dhananjaya.dhananjaya.doctype.donation_receipt.operations.receipt_cash_return_operations",
                      args: {
                        receipt: frm.doc.name,
                        cash_return_date: values.returned_date,
                      },
                      callback: function (r) {
                        if (!r.exc) {
                          frappe.msgprint("Successfully Returned.");
                        }
                      },
                    });
                  }
                );
              },
              () => {}
            );
          },
          "Operations"
        );
      }
    }
    frm.add_custom_button(
      __("Send Receipt/Acknowledgement"),
      async function () {
        donor_doc = await frappe.db.get_doc("Donor", frm.doc.donor);
        if (donor_doc.emails.length == 0) {
          frappe.prompt(
            {
              label: "Provide Email",
              fieldname: "email",
              fieldtype: "Data",
              options: "Email",
            },
            (values) => {
              frm.events.send_receipt_email(frm, values.email);
            }
          );
        } else {
          frappe.prompt(
            {
              label: "Select Email",
              fieldname: "email",
              fieldtype: "Select",
              options: donor_doc.emails.map((item) => item.email),
            },
            (values) => {
              frm.events.send_receipt_email(frm, values.email);
            }
          );
        }
      },
      "Operations"
    );

    frm.add_custom_button(
      __("Bounce"),
      function () {
        var warning_message = "";
        if (frm.doc.bounce_transaction) {
          warning_message =
            "This action will consequently create a bounced Journal Entry and reconcile the Bank Statement as well.";
        } else {
          warning_message =
            "This action will directly put the receipt in Bounced State without going through Realization.";
          if (frm.doc.docstatus == 1) {
            frappe.msgprint(
              "Bounce Transaction is mandatory for Realized State"
            );
            return;
          }
        }

        frappe.warn(
          "Are you sure you want to proceed to bounce this Cheque Donation?",
          warning_message,
          () => {
            frappe.call({
              freeze: true,
              freeze_message: "Bouncing Cheque Donation",
              method:
                "dhananjaya.dhananjaya.doctype.donation_receipt.operations.receipt_bounce_operations",
              args: {
                receipt: frm.doc.name,
              },
              callback: function (r) {
                if (!r.exc) {
                  frappe.msgprint("Successfully Bounced.");
                }
              },
            });
          },
          () => {}
        );
      },
      "Operations"
    );

    frm.add_custom_button(__("PDF"), function () {
      let print_format = "80G Receipt";
      window.open(
        `/api/method/dhananjaya.dhananjaya.utils.download_pdf?doctype=Donation Receipt&name=${frm.doc.name}&format=${print_format}`
      );
    });
  },
  send_receipt_email(frm, recipient) {
    frappe.call({
      freeze: true,
      freeze_message: "Sending...",
      method:
        "dhananjaya.dhananjaya.doctype.donation_receipt.donation_receipt.send_receipt",
      args: {
        dr: frm.doc.name,
        recipients: recipient,
      },
      callback: function (r) {
        if (!r.exc) {
          frappe.msgprint("Successfully Sent.");
        } else {
          console.log(r.message);
        }
      },
    });
  },
  bank_transaction: function (frm) {
    if (!frm.doc.bank_account) {
      frappe.msgprint("Please select first the Bank Account for transactions.");
      frm.set_value("bank_transaction", null);
    }
  },
  payment_gateway_document: async function (frm) {
    if (frm.doc.payment_gateway_document) {
      var gateway_doc = await frappe.db.get_doc(
        "Payment Gateway Transaction",
        frm.doc.payment_gateway_document
      );
      frm.set_value("additional_charges", gateway_doc.fee);
      console.log(gateway_doc);
      var bank_account_doc = await frappe.db.get_doc(
        "PG Upload Batch",
        gateway_doc.batch
      );
      frm.set_value("bank_account", bank_account_doc.bank_account);
      frm.set_value("bank_transaction", bank_account_doc.bank_transaction);
      frm.set_value(
        "gateway_expense_account",
        bank_account_doc.gateway_expense_account
      );
      frm.save();
    } else {
      frm.set_value("additional_charges", 0);
      frm.set_value("bank_account", null);
      frm.set_value("bank_transaction", null);
      frm.save();
    }
  },
  seva_type: function (frm) {
    frm.events.update_donation_income_account(frm);
  },
  seva_subtype: function (frm) {
    frm.events.update_cost_center(frm);
  },
  is_csr: function (frm) {
    frm.events.update_donation_income_account(frm);
  },
  async update_donation_income_account(frm) {
    if (frm.doc.docstatus == 0) {
      var separate_accounting_for_csr = await frappe.db.get_single_value(
        "Dhananjaya Settings",
        "separate_accounting_for_csr"
      );
      var account_key;
      if (frm.doc.is_csr && separate_accounting_for_csr) {
        account_key = "csr_account";
      } else {
        account_key = "account";
      }
      frappe.db.get_value(
        "Seva Type",
        { name: frm.doc.seva_type },
        account_key,
        (r) => {
          frm.set_value("donation_account", r[account_key]);
          if (!frm.doc.donation_account) {
            frappe.throw("There is no account set in Seva Type.");
          }
        }
      );
    }
  },
  async update_cost_center(frm) {
    if (frm.doc.docstatus == 0) {
      frappe.call({
        method: "frappe.client.get",
        args: {
          doctype: "Seva Subtype",
          name: frm.doc.seva_subtype,
          fieldname: "cost_centers",
        },
        callback(r) {
          if (r.message) {
            cost_centers = r.message.cost_centers;
            for (var i = 0; i < cost_centers.length; i++) {
              if (frm.doc.company == cost_centers[i].company) {
                frm.set_value("cost_center", cost_centers[i].cost_center);
                break;
              }
            }
          }
        },
      });
    }
  },
});
