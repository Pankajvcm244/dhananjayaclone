frappe.listview_settings['Payment Gateway Transaction'] = {
	add_fields: [ "receipt_created"],
	get_indicator: function(doc) {
		if (doc.receipt_created==1) {
			return [__("Created"), "green", "receipt_created,=,Created"];
		}
		else {
			return [__("Pending"), "orange", "receipt_created,=,Pending"];
		}
	}
};