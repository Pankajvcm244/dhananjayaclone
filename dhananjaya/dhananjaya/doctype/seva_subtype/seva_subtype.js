// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on('Seva Subtype', {
	onload: function (frm) {
		frm.set_query("parent_seva_subtype", function () {
			return {
				filters: {
					enabled: 1,
					is_group: 1,
					name: ["!=", frm.doc.name]
				}
			}
		});

		frm.set_query("parent_seva_subtype", function () {
			return {
				filters: {
					enabled: 1,
					is_group: 1,
					name: ["!=", frm.doc.name]
				}
			}
		});

		frm.set_query("cost_center", "cost_centers", function (doc, cdt, cdn) {
			let d = locals[cdt][cdn];
			return {
				filters: [
					['Cost Center', 'disabled', '=', 0],
					['Cost Center', 'company', '=', d.company]
				]
			};
		});

	},
});
