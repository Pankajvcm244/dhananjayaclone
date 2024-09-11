// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on('PG Upload Tool', {
	refresh: function (frm) {
		frm.add_custom_button(__('Upload Gateway'), function () {
			if (frm.is_dirty()) {
				frappe.show_alert('Please save form before processing.')
			}
			else {
				frappe.call({
					freeze: true,
					freeze_message: "Uploading Trasactions.",
					method: "dhananjaya.dhananjaya.doctype.pg_upload_tool.pg_upload_tool.upload_gateway_transactions",
					callback: function (r) {
						if (!r.exc) {
							frappe.msgprint("Uploaded. Please Check Once.");
						}
					}
				});
			}
		});
	}
});