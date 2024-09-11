// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on('Donor Festival Benefit', {
	refresh: function(frm) {
		frm.set_query('donation_receipt',()=> {
			return {
				filters: {
					donor : frm.doc.donor,
					docstatus: 1
				}
			}
		});
		frm.set_query('festival_benefit',()=> {
			return {
				filters: {
					festival : frm.doc.festival,
					docstatus: 1
				}
			}
		});
	}
});
