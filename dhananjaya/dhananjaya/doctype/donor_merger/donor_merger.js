// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on('Donor Merger', {
	onload:function(frm){
		frm.events.set_html_data('first',frm);
		frm.events.set_html_data('second',frm);
	},
	refresh: function(frm) {
		frm.set_query('donor_first',() => {
			return {
				filters: {
					name:["!=",frm.doc.donor_second]
				}
			}
		});
		frm.set_query('donor_second',() => {
			return {
				filters: {
					name:["!=",frm.doc.donor_first]
				}
			}
		});

		if(!(frm.is_dirty())){
			frm.page.set_primary_action(__("Merge"), function() {
				if(!frm.doc.priority_first && !frm.doc.priority_second){
					frappe.throw(__('Please select at least one donor for Priority'));
				}else{
					var elements_address = [];
					var elements_contact = []; 
					var adds = JSON.parse(frm.doc.data_first).addresses.concat(JSON.parse(frm.doc.data_second).addresses)
					var cts = JSON.parse(frm.doc.data_first).contacts.concat(JSON.parse(frm.doc.data_second).contacts)
					
					adds.forEach((element,ind)=>{
						var preferred_string = "";
						if(element.preferred == 1){
							preferred_string = "✔️";
						}
						elements_address.push({
							fieldname: element.name,
							label: preferred_string + element.type + ': ' + element.address_line_1 + element.address_line_2 + element.city,
							fieldtype: 'Check',
							default:1
						})
					})
					cts.forEach((element,ind)=>{
						elements_contact.push({
							fieldname: element.name,
							label: element.contact_no,
							fieldtype: 'Check',
							default:1
						})
					})
					
					let d = new frappe.ui.Dialog({
						title: 'Choose Addresses to keep:',
						fields: elements_address,
						primary_action_label: 'Proceed',
						primary_action(address_values) {
							let c_dialog = new frappe.ui.Dialog({
								title: 'Choose Contacts to keep:',
								fields: elements_contact,
								primary_action_label: 'Proceed',
								primary_action(contact_values) {
									c_dialog.hide();
									frappe.warn('Are you sure you want to proceed?',
										'Once merged, it can\'t be undone.',
										() => {
											frm.call({
												freeze:true,
												freeze_message:"Merging...!!!",
												method:'dhananjaya.dhananjaya.doctype.donor_merger.donor_merger.merge_donors',
												args:{
													donor_first:frm.doc.donor_first,
													donor_second:frm.doc.donor_second,
													priority_first:frm.doc.priority_first,
													priority_second:frm.doc.priority_second,
													address_values:Object.keys(address_values).filter(key => address_values[key] === 1),
													contact_values:Object.keys(contact_values).filter(key => contact_values[key] === 1),
												},
												callback:function(r){
													if(!r.exc){
														frappe.msgprint("Successfully Merged.")
													}
												}
											});
										},
										'Continue',
										true // Sets dialog as minimizable
									)
									
								}
							});
							c_dialog.show();
							d.hide();
						}
					});
					
					d.show();
				}
			});
		}else{
			frm.page.set_primary_action(__("Save"), () => frm.save());
		}
	},
	donor_first:function(frm){
		frm.events.set_html_data('first',frm);
	},
	donor_second:function(frm){
		frm.events.set_html_data('second',frm);
	},
	set_html_data(index,frm){
		if(!frm.doc["donor_"+index]){
			frm.set_value('data_'+index,"");
			frm.set_df_property('data_'+index+'_html', 'options', "No Data");
			frm.refresh_field('data_'+index+'_html');
			return;
		}
		frm.call({
			method:'dhananjaya.dhananjaya.doctype.donor_merger.donor_merger.get_donor_details',
			args:{
				donor:frm.doc["donor_"+index]
			},
			callback:function(r){
				if(!r.exc){
					var data = JSON.parse(r.message);
					frm.set_value('data_'+index,r.message);
					var addresses = "";
					var contacts = "";
					var emails = "";
					data['addresses'].forEach((val,ind)=>{
						var preferred_string = "";
						if(val.preferred == 1){
							preferred_string = "✔️";
						}
						addresses += `<p>${preferred_string} ${ind+1}. <${val.type}> ${val.address_line_1} ${val.address_line_2} ${val.city}</p>`;
					});
					data['contacts'].forEach((val,ind)=>{
						contacts += `<p>${ind+1}. ${val.contact_no}</p>`;
					});
					data['emails'].forEach((val,ind)=>{
						emails += `<p>${ind+1}. ${val.email}</p>`;
					});
					
					var html = `
						Donor ID : ${frm.doc["donor_"+index]}<br>
						<h6>Name: ${data.full_name}</h6>
						<h6>Preacher: ${data.llp_preacher}</h6>
						<h6>Addresses:</h6>
							${addresses}
						<h6>Contacts:</h6>
							${contacts}
						<h6>Emails:</h6>
							${emails}
						<h6>KYC:</h6>
							<p>PAN : ${data.pan_no}</p>
							<p>Aadhar : ${data.aadhar_no}</p>
							<p>Driving License : ${data.driving_license}</p>
							<p>Passport : ${data.passport}</p>
					`
					frm.set_df_property('data_'+index+'_html', 'options', html);
					// frm.refresh_field('data_'+index);
					frm.refresh();
				}
			}
		});
	}
});
