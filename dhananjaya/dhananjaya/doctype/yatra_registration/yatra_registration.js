// Copyright (c) 2024, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on("Yatra Registration", {
  refresh(frm) {
    frm.set_query("seva_subtype", () => {
      return {
        filters: {
          is_a_yatra: 1,
          enabled: 1,
        },
      };
    });
    frm.set_query("donor_creation_request",  () => {
      return {
        filters: {
          status: "Open",
          docstatus: 1
        },
      };
    });
    // if (!frm.is_new()) {
    //   getTotalPaidAmount(frm);
    // }
  },


  onload(frm) {
    if (!frm.is_new()) {
      getTotalPaidAmount(frm);
    }
   
  },


});


function getTotalPaidAmount(frm){
  frappe.call({
      method: "dhananjaya.api.v1.yatra.get_total_paid_amount",
      args: {
        seva_subtype: frm.doc.seva_subtype,
        booking: frm.doc.name
          
      },
      freeze: true,
      async: true,
      callback: function(r) {
          if(r.message) {
            console.log(r.message);
              
              frm.doc.received_amount = r.message
          }
          else {
            var r = "00"
            frm.doc.received_amount = r
          }
      }
  });

}
