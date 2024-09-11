// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on('ECS Upload Portal', {
	refresh: function (frm) {

		frm.set_query('seva_type', () => {
			return {
				filters: {
					company: frm.doc.company,
					enabled: 1
				}
			}
		});

		frm.events.fetch_sheets_data(frm);
		if (frm.doc.bank_transaction && frm.google_sheets_url) {
			frm.page.set_primary_action(__('Process'), () => frm.events.process_data(frm));
		}
		frm.set_query('bank_transaction', () => {
			return {
				filters: {
					status: 'Unreconciled',
					deposit: frm.doc.final_amount
					// date: ['>=',frm.doc.receipt_date]
				}
			}
		});
	},
	process_data(frm) {
		frm.call({
			freeze: true,
			freeze_message: "Processing",
			method: 'dhananjaya.dhananjaya.doctype.ecs_upload_portal.ecs_upload_portal.process_ecs_data',
			callback: function (r) {
				if (!r.exc) {
					frappe.msgprint(__('Successfully Done.'));
				} else {
					console.log(r.data);
					frappe.msgprint(__('Failed.'));
				}
			}
		});
	},
	google_sheets_url(frm) {
		console.log("calling");
		frm.events.fetch_sheets_data(frm);
	},

	fetch_sheets_data(frm) {
		frm.call({
			freeze: true,
			freeze_message: "Loading",
			method: 'dhananjaya.dhananjaya.doctype.ecs_upload_portal.ecs_upload_portal.fetch_data',
			callback: function (r) {
				if (!r.exc) {

					var html = frm.events.get_html_data(frm, r.message);
					frm.set_df_property('data_view', 'options', html);

				}
			}
		});
	},

	get_html_data(frm, data) {
		var data = JSON.parse(data);
		var headers = Object.keys(data[0]);
		var header_html = "";
		headers.forEach((v) => {
			header_html += `<th>${v}</th>`;
		});

		var analysis = {
			"total_count": 0,
			"success": 0,
			"total_success_amount": 0
		}

		var data_html = "";
		for (let d in data) {
			let row_html = "";
			let failed_style = "";
			analysis['total_count'] += 1;
			if (data[d]['Reason Code'] != 0) {
				failed_style = ` style = 'background-color:red; color: white '`;
			} else {
				analysis['success'] += 1;
				analysis['total_success_amount'] += parseInt(data[d]['Amount']);
			}
			Object.values(data[d]).forEach((v) => {
				row_html += `<td>${v}</td>`;
			});
			row_html = `<tr${failed_style}>${row_html}</tr>`;
			data_html += row_html;
		}

		var html = `
					<style>
						table {
							border-collapse: collapse;
							width: 100%;
						}
						
						th, td {
							border: 1px solid black;
							padding: 10px;
							text-align: left;
						}
					</style>
					<div style ="display:flex; justify-content: space-between; ">
						<div style = "padding-inline: 5px; margin-block: 5px;border: 0px solid;  border-radius: 5px; background-color: green; display: flex; justify-content: center;">
							<h2 style = 'color:white;'>
								Cummulative Amount = ₹ ${analysis['total_success_amount']}	
							</h2>
						</div>
						<h2>
							Count = ${analysis['success']} / ${analysis['total_count']}
						</h2>
					</div>

					
					
					<table>
						<thead>
							<tr>
								${header_html}
							</tr>
						</thead>
						<tbody>
								${data_html}
						</tbody>
					</table>`
		if (analysis['success'] > 0) {
			frm.set_df_property('bank_transaction', 'hidden', false);
			frm.page.set_primary_action(__('Process'), () => frm.events.process_data(frm));
			frm.set_value("final_amount", analysis['total_success_amount']);
			frm.refresh_field('final_amount');
		}
		return html;

	}
});
