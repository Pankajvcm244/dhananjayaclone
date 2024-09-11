// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on('Patron', {
	refresh: function (frm) {
		if (!frm.is_new()) {
			frappe.call({
				'method': 'dhananjaya.dhananjaya.doctype.patron.patron.get_patron_status',
				'args': {
					'patron': frm.doc.name
				},
				'callback': function (res) {
					console.log(res);
					var template = frm.events.update_status_html(frm, res.message);
					frm.set_df_property('patron_status_html', 'options', template);
					frm.refresh_field('patron_status_html');
				}
			})
		}
	},
	update_status_html(frm, data) {
		var html = `
		<div style="display: flex; justify-content: space-around; margin: 20px;">

			<div style="color:rgb(35 15 128);padding: 10px; border: 1px solid #ccc; border-radius: 5px; width: 30%;">
				<p>Committed Amount</p>
				<p style="font-weight: bold; margin-top: 10px;"> ${frm.events.formatMoney(frm.doc.committed_amount)}</p>
			</div>

			<div style="color:green; padding: 10px; border: 1px solid #ccc; border-radius: 5px; width: 30%;">
				<p>Completed Amount</p>
				<p style="font-weight: bold; margin-top: 10px;"> ${frm.events.formatMoney(data['completed'])}</p>
			</div>

			<div style="color:hsl(0deg 80.54% 32.36%); padding: 10px; border: 1px solid #ccc; border-radius: 5px; width: 30%;">
				<p>Remaining Amount</p>
				<p style="font-weight: bold; margin-top: 10px;"> ${frm.events.formatMoney(frm.doc.committed_amount - data['completed'])}</p>
			</div>
		</div>

		`
		return html
	},
	formatMoney(amount) {
		return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount);
	},
});
