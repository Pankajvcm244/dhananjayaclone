frappe.listview_settings['Donor Creation Request'] = {
	// add_fields: ["base_grand_total", "customer_name", "currency", "delivery_date",
	// 	"per_delivered", "per_billed", "status", "order_type", "name", "skip_delivery_note"],
	get_indicator: function (doc) {
		if (doc.status === "Closed") {
			// Closed
			return [__("Closed"), "green", "status,=,Closed"];
		} else if (doc.status === "Open") {
			// open
			return [__("Open"), "orange", "status,=,Open"];
		} else if (doc.status === "Rejected") {
			return [__("Rejected"), "red", "status,=,Rejected"];
		} else if(doc.docstatus == 2){
            return [__("Cancelled"), "red", "status,=,Cancelled"];
        }
	}
};