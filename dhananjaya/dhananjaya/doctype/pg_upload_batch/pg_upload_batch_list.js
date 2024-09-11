// frappe.listview_settings['PG Upload Batch'] = {
// 	add_fields: ["status"],
// 	get_indicator: function(doc) {
// 		if(doc.final_amount == 0) {
// 			return [__("Closed"), "green", "status,=,Closed"];
// 		}
//         else if(doc.final_amount != 0) {
// 			return [__("Open"), "red", "status,=,Open"];
// 		}
// 	}
// }