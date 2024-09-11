// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt

var donor_path = "dhananjaya.dhananjaya.doctype.dhananjaya_import_settings.import_donors."
var receipt_path = "dhananjaya.dhananjaya.doctype.dhananjaya_import_settings.import_receipts."
var patron_path = "dhananjaya.dhananjaya.doctype.dhananjaya_import_settings.import_patrons."

frappe.ui.form.on('Dhananjaya Import Settings', {
	setup:function(frm){
		frm.get_field("patron_correction_template_file").df.options = {
			restrictions: {
				allowed_file_types: [".csv"],
			},
		};
	},
	refresh: function(frm) {
			var donor_import_button = ['Preachers','Countries','Salutations'];
			for(let btn in donor_import_button){
				frm.add_custom_button(__('Import '+donor_import_button[btn]), function(){
					frappe.call({
						freeze:true,
						freeze_message:"Importing "+donor_import_button[btn],
						method: donor_path+"import_"+donor_import_button[btn].toLowerCase(),
						callback: function(r) {
							if(!r.exc){
								frappe.msgprint("Successfully Imported");
							}
						}
					});
				}, __("Donor Import Buttons"));
			}
			frm.add_custom_button(__('Import Donors'), function(){
				frappe.call({
					freeze:true,
					freeze_message:"Importing Donors",
					method: donor_path+"import_donors",
					callback: function(r) {
						if(!r.exc){
							frappe.msgprint("Successfully Imported");
						}
					}
				});
			}, __("Donor Import Buttons"));
			frm.add_custom_button(__('Set Patron ID in Donors'), function(){
				frappe.call({
					freeze:true,
					freeze_message:"Setting Patron ID in Donors.",
					method: donor_path+"set_patron_in_donors",
					callback: function(r) {
						if(!r.exc){
							frappe.msgprint("Successfully Set.");
						}
					}
				});
			});
			frm.add_custom_button(__('Set Latest Preacher in Donors'), function(){
				frappe.call({
					freeze:true,
					freeze_message:"Setting Latest Preacher in Donors.",
					method: donor_path+"set_latest_preacher_in_donors",
					callback: function(r) {
						if(!r.exc){
							frappe.msgprint("Successfully Set.");
						}
					}
				});
			});
			var receipts_import_button = ['Sevas','Subsevas','Mode_of_Payment','Receipts'];
			for(let btn in receipts_import_button){
				frm.add_custom_button(__('Import '+receipts_import_button[btn]), function(){
					frappe.call({
						freeze:true,
						freeze_message:"Importing "+receipts_import_button[btn],
						method: receipt_path+"import_"+receipts_import_button[btn].toLowerCase(),
						callback: function(r) {
							if(!r.exc){
								frappe.msgprint("Successfully Imported");
							}
						}
					});
				}, __("Receipt Import Buttons"));  //import_receipts
			}
			// frm.add_custom_button(__('Import Receipts'), function(){
			// 	frappe.call({
			// 		freeze:true,
			// 		freeze_message:"Importing Donors",
			// 		method: receipt_path+"import_receipts",
			// 		callback: function(r) {
			// 			if(!r.exc){
			// 				frappe.msgprint("Successfully Imported");
			// 			}
			// 		}
			// 	});
			// }, __("Receipt Import Buttons"));

			var patron_import_buttons = ['Grade','Patron_seva','Patrons'];
			for(let btn in patron_import_buttons){
				frm.add_custom_button(__('Import '+patron_import_buttons[btn]), function(){
					frappe.call({
						freeze:true,
						freeze_message:"Importing "+patron_import_buttons[btn],
						method: patron_path+"import_"+patron_import_buttons[btn].toLowerCase(),
						callback: function(r) {
							if(!r.exc){
								frappe.msgprint("Successfully Imported");
							}
						}
					});
				}, __("Patron Import Buttons"));  //import_receipts
			}
			frm.add_custom_button(__('Update Donation Patron'), function(){
				frappe.call({
					freeze:true,
					freeze_message:"Setting Up... ",
					method: patron_path+"set_patron_in_donations",
					callback: function(r) {
						if(!r.exc){
							frappe.msgprint("Successfully Imported");
						}
					}
				});
			}, __("Patron Import Buttons")); 
			frm.add_custom_button(__('Update Gifts'), function(){
				frappe.call({
					freeze:true,
					freeze_message:"Setting Up... ",
					method: patron_path+"update_gifts_in_patron",
					callback: function(r) {
						if(!r.exc){
							frappe.msgprint("Successfully Imported");
						}
					}
				});
			}, __("Patron Import Buttons")); 
	},
	export_defective_patron_data:function(frm){
		open_url_post(
			"/api/method/dhananjaya.dhananjaya.doctype.dhananjaya_import_settings.import_donors.export_defective_patrons",{}
		)
	},
	download_patron_correction_template:function(frm){
		open_url_post(
			"/api/method/dhananjaya.dhananjaya.doctype.dhananjaya_import_settings.import_donors.download_patron_correction_template"
		)
	},
	download_donor_data:function(frm){
		open_url_post(
			"/api/method/dhananjaya.dhananjaya.doctype.dhananjaya_import_settings.operations.get_data_for_analysis",{}
		)
	},
	download_template_for_merging:function(frm){
		open_url_post(
			"/api/method/dhananjaya.dhananjaya.doctype.dhananjaya_import_settings.operations.get_template_for_merging_donors",{}
		)
	}, 
	merge_donors:function(frm){
		open_url_post(
			"/api/method/dhananjaya.dhananjaya.doctype.dhananjaya_import_settings.operations.merge_donors",{}
		)
	}, 
	upload_patron_correction_template:function(frm){
		frappe.call({
			freeze:true,
			freeze_message:"Updating Donors.",
			method: donor_path+"upload_patron_correction_template",
			callback: function(r) {
				if(!r.exc){
					frappe.msgprint("Updated. Please Check Once.");
				}
			}
		});
	}
});
