// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on("PG Upload Batch", {
  onload: function (frm) {
    frm.events.set_finalview(frm);
  },
  refresh: function (frm) {
    frm.set_query("gateway_expense_account", () => {
      return {
        filters: {
          company: frm.doc.company,
          root_type: "Expense",
          is_group: 0,
        },
      };
    });
    frm.set_query("bank_transaction", () => {
      return {
        filters: {
          status: "Unreconciled",
          unallocated_amount: frm.doc.remaining_amount,
          bank_account: frm.doc.bank_account,
          // date: ['>=',frm.doc.receipt_date]
        },
      };
    });
    frm.add_custom_button(
      __("Set Seva Type (BULK)"),
      function () {
        frappe.prompt(
          {
            label: "Seva Type",
            fieldname: "seva_type",
            fieldtype: "Link",
            options: "Seva Type",
          },
          (values) => {
            // console.log(values.seva_type);
            frappe.call({
              freeze: true,
              freeze_message: "Processing...",
              method:
                "dhananjaya.dhananjaya.doctype.pg_upload_batch.pg_upload_batch.set_seva_type_bulk",
              args: {
                batch: frm.doc.name,
                seva_type: values.seva_type,
              },
              callback: function (r) {
                if (!r.exc) {
                  frappe.show_alert(
                    "Successfully set Seva Type in all connected payments",
                    5
                  );
                }
              },
            });
          }
        );
      },
      "Operations"
    );
    frm.add_custom_button(
      __("Process Batch Payments"),
      function () {
        frappe.warn(
          "Are you sure you want to proceed?",
          "This will generate following:<br><br>1. Donation Entries<br>2. Journal Entries<br>3. Bank Reconcillation",
          () => {
            frappe.call({
              freeze: true,
              freeze_message: "Processing...",
              method:
                "dhananjaya.dhananjaya.doctype.donation_receipt.donation_receipt.process_batch_gateway_payments",
              args: {
                batch: frm.doc.name,
              },
              callback: function (r) {
                if (!r.exc) {
                  frappe.msgprint("Successfully Created.");
                  frm.refresh();
                  frm.refresh_field("status");
                }
              },
            });
          },
          "Continue",
          true // Sets dialog as minimizable
        );
      },
      "Operations"
    );
    frm.add_custom_button(
      __("Auto Realize Receipts"),
      function () {
        frappe.warn(
          "Are you sure you want to proceed?",
          "This will check for Donation Receipts which have Transaction ID in 'Remarks' field and realize them.",
          () => {
            frappe.call({
              freeze: true,
              freeze_message: "Processing...",
              method:
                "dhananjaya.dhananjaya.doctype.donation_receipt.donation_receipt.auto_realize_batch_gateway_payments",
              args: {
                batch: frm.doc.name,
              },
              callback: function (r) {
                if (!r.exc) {
                  frappe.msgprint("Successfully Connected.");
                  frm.refresh();
                }
              },
            });
          },
          "Continue",
          true // Sets dialog as minimizable
        );
      },
      "Operations"
    );
    frm.add_custom_button(
      __("Check Receipts"),
      function () {
        frappe.call({
          method:
            "dhananjaya.dhananjaya.doctype.pg_upload_batch.pg_upload_batch.get_payment_entries",
          args: {
            batch: frm.doc.name,
          },
          callback: function (r) {
            if (!r.exc) {
              console.log(r.message);
              frappe.set_route("List", "Donation Receipt", {
                payment_gateway_document: ["in", r.message],
              });
            }
          },
        });
      },
      "Receipts"
    );
    frm.add_custom_button(
      __("Disconnect Cancelled Receipts"),
      function () {
        frappe.call({
          method:
            "dhananjaya.dhananjaya.doctype.pg_upload_batch.pg_upload_batch.disconnect_cancelled_receipts",
          args: {
            batch: frm.doc.name,
          },
          callback: function (r) {
            if (!r.exc) {
              frappe.show_alert({
                message: __("Successfully disconnected"),
                indicator: "green",
              });
              frm.refresh();
            } else {
              frappe.show_alert({
                message: __("Couldn't disconnect."),
                indicator: "red",
              });
            }
          },
        });
      },
      "Receipts"
    );
    frm.add_custom_button(
      __("Try Razorpay Pattern"),
      function () {
        frappe.call({
          freeze: true,
          freeze_message: "Setting Up",
          method:
            "dhananjaya.dhananjaya.doctype.pg_upload_batch.setting_donors.try_razorpay_pattern",
          args: {
            batch: frm.doc.name,
          },
          callback: function (r) {
            if (!r.exc) {
              console.log(r.message);
            }
          },
        });
      },
      "Setting Donors"
    );
    frm.add_custom_button(
      __("Try AU QR Pattern"),
      function () {
        frappe.call({
          freeze: true,
          freeze_message: "Setting Up",
          method:
            "dhananjaya.dhananjaya.doctype.pg_upload_batch.setting_donors.try_au_qr_pattern",
          args: {
            batch: frm.doc.name,
          },
          callback: function (r) {
            if (!r.exc) {
              console.log(r.message);
            }
          },
        });
      },
      "Setting Donors"
    );
    frm.add_custom_button(
      __("Try Standard Pattern"),
      function () {
        frappe.call({
          freeze: true,
          freeze_message: "Setting Up",
          method:
            "dhananjaya.dhananjaya.doctype.pg_upload_batch.setting_donors.try_standard_pattern",
          args: {
            batch: frm.doc.name,
          },
          callback: function (r) {
            if (!r.exc) {
              console.log(r.message);
            }
          },
        });
      },
      "Setting Donors"
    );
  },
  bank_transaction: function (frm) {
    frm.events.set_finalview(frm);
  },
  // async recalculate_amounts(frm) {
  //   var total_amount = 0;
  //   var total_fee = 0;
  //   var txs = await frappe.db.get_list("Payment Gateway Transaction", {
  //     fields: ["name", "amount", "fee"],
  //     filters: [
  //       ["batch", "=", frm.doc.name],
  //       ["receipt_created", "=", 0],
  //     ],
  //     limit: 10000,
  //   });

  //   await txs.forEach((element) => {
  //     total_amount += element["amount"];
  //     total_fee += element["fee"];
  //   });
  //   // console.log(total_amount);
  //   // console.log(total_amount.toFixed(2));

  //   frm.set_value("total_amount", total_amount.toFixed(2));
  //   frm.set_value("total_fee", total_fee.toFixed(2));
  //   frm.set_value("remaining_amount", (total_amount - total_fee).toFixed(2));
  //   if (frm.doc.bank_transaction) {
  //     var amount = await frappe.db.get_value(
  //       "Bank Transaction",
  //       frm.doc.bank_transaction,
  //       "unallocated_amount"
  //     );
  //     console.log(amount["message"]["unallocated_amount"]);
  //     frm.set_value("bank_amount", amount["message"]["unallocated_amount"]);
  //   }

  //   if (frm.is_dirty()) {
  //     frm.save();
  //   }
  // },
  async set_finalview(frm) {
    frappe.call({
      method:
        "dhananjaya.dhananjaya.doctype.pg_upload_batch.pg_upload_batch.count_donor_linked",
      args: {
        batch: frm.doc.name,
      },
      callback: function (r) {
        if (!r.exc) {
          console.log(r);
          var diff_amount = frm.doc.bank_amount - frm.doc.remaining_amount;
          var add_html = "";
          if (diff_amount == 0) {
            frm.se;
            add_html = '<h3 class="p-1" style = "color:green"> ELIGIBLE </h3>';
          } else {
            add_html =
              '<h3 class="p-1" style = "color:red"> NOT-ELIGIBLE </h3>';
          }

          var dataview = `
							<div style="margin:5px">
								<div class ="d-flex justify-content-between">
                  <div class= "border rounded p-2 w-40" style="font-size:15px">
										Transactions<p style="font-size:10px">(Resolved/Total)</p><b>${r.message[1]}/${
            r.message[0]
          }</b>
									</div>
                  <div class= "border rounded p-2 w-40" style="font-size:15px">
										Donors Linked<p style="font-size:10px">(Linked/Unresolved)</p><b>${
                      r.message[2]
                    }/${r.message[0] - r.message[1]}</b>
									</div>
								</div>
                <hr>
								<div class="d-flex justify-content-between">
									<div class="p-2">Amount as Per Gateway</div>
									<div class="p-2"> ₹ ${frm.doc.remaining_amount}</div>
								</div>
                <div class="d-flex justify-content-between">
									<div class="p-2">Amount as Per Bank</div>
									<div class="p-2"> ₹ ${frm.doc.bank_amount}</div>
								</div>
								<hr>
								<div class="d-flex justify-content-between">
									<div class="p-2">Difference</div>
									<div class="p-2"> ₹ <b>${diff_amount}</b></div>
								</div>
								<div class ="d-flex justify-content-center">
									${add_html}
								</div>
							</div>
							`;
          frm.set_df_property("final_view", "options", dataview);
          frm.refresh_field("final_view");
        }
      },
    });
  },
});
