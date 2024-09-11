// Copyright (c) 2024, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on("DJ Bank Operations", {
	refresh(frm) {

	},
    process_bulk_vendor_payment(frm){
        frm.call({
			freeze: true,
            method:"POST",
			freeze_message: "Processing",
			method: 'dhananjaya.dhananjaya.doctype.dj_bank_operations.vendor_payment.process',
			callback: function (r) {
				if (!r.exc) {
					frappe.msgprint(__('Successfully Done.'));
				} else {
					console.log(r.data);
					frappe.msgprint(__('Failed.'));
				}
			}
		});
    }
});
