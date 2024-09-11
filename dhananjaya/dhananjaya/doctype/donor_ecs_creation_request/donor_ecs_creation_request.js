// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on('Donor ECS Creation Request', {
	refresh: function(frm) {
		frm.set_query('seva_type',()=> {
			return {
				filters: {
					company : frm.doc.company,
					enabled : 1
				}
			}
		});
	}
});
