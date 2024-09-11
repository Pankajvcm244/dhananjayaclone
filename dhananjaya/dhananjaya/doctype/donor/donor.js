// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on('Donor', {
	refresh: function(frm) {
		frm.add_custom_button(__("Create Patron"), function(){
			frappe.model.open_mapped_doc({
				method: "dhananjaya.dhananjaya.doctype.donor.donor.create_patron_from_donor",
				frm: frm,
				run_link_triggers: true
			});
		  });
	}
});
