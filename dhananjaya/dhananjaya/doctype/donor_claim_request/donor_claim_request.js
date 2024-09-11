// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on('Donor Claim Request', {
	refresh: function (frm) {
		frm.add_custom_button(__('Update Preacher'), function () {
			frappe.prompt({
				label: 'Preacher',
				fieldname: 'preacher',
				fieldtype: 'Link',
				options: 'LLP Preacher',
				default: frm.doc.preacher_claimed
			}, (values) => {
				frappe.call({
					freeze: true,
					freeze_message: "Setting Preacher",
					method: "dhananjaya.dhananjaya.doctype.donor_claim_request.donor_claim_request.update_preacher",
					args: {
						request: frm.doc.name,
						preacher: values.preacher
					},
					callback: function (r) {
						if (!r.exc) {
							frappe.msgprint("Successfully Updated");
							frm.set_value('status', 'Approved');
							frm.save();
						}
					}
				});
			})
		},);
		frm.add_custom_button(__('Reject'), function () {
			frappe.confirm('Are you sure you want to proceed?',
				() => {
					frm.set_value('status', 'Rejected');
					frm.save();
				}, () => {

				})
		},);
	}
});
