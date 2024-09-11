// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on('Dhananjaya Bank Statement Upload', {
	setup: function(frm){
		frm.has_import_file = () => {
			return frm.doc.google_sheets_link;
		};
	},
	refresh: function(frm) {
		frm.add_custom_button(__('Upload'), function(){
			frm.events.start_import(frm);
		});
	},
	// update_primary_action(frm) {
	// 	if (frm.is_dirty()) {
	// 		frm.page.set_primary_action(__("Save"), () => frm.save());
	// 		return;
	// 	}else{
	// 		frm.page.set_primary_action(label, () => frm.events.start_import(frm));
	// 	}
	// },
	start_import(frm) {
		frm.call({
			freeze:true,
			freeze_message:"Uploading Statements.",
			method: "dhananjaya.dhananjaya.doctype.dhananjaya_bank_statement_upload.dhananjaya_bank_statement_upload.bank_statement_upload",
			args: { data_import: frm.doc.name },
			btn: frm.page.btn_primary,
		}).then((r) => {
			console.log(r);
			if (r.message === true) {
				frappe.msgprint("Successfully Uploaded. Please check once.")
			}
		});
	},
	// google_sheets_link(frm) {
	// 	frm.trigger("update_primary_action");
	// },
});
