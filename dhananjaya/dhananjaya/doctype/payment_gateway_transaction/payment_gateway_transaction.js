// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Gateway Transaction', {
	refresh: function (frm) {
		var dataview = frm.events.get_dataview(frm.doc.extra_data);
		frm.set_df_property('view_extra', 'options', dataview);
		frm.refresh_field('view_extra');
		frm.set_query("seva_type", () => {
			return {
				filters: {
					company: frm.doc.company,
					enabled: 1
				},
			};
		});
	},
	get_dataview(data) {
		var template = "<table class=\"table table-bordered table-sm\"><tbody><tr><th>#</th><th>Field</th><th>Value</th></tr>";
		let x = 1
		data = JSON.parse(data);
		for (var key in data) {
			if (data[key] && data[key] != 0) {
				template += '<tr><td>' + (x++) + '</td><td>' + key + '</td><td>' + data[key] + '</td></tr>';
			}

		}
		template += "</tbody></table>";
		return template
	}
});
