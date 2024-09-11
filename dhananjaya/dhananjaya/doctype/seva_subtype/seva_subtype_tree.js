frappe.treeview_settings["Seva Subtype"] = {
	breadcrumb: "Seva Subtypes",
	get_tree_root: false,
	root_label: "All Types",
	get_tree_nodes: "dhananjaya.dhananjaya.doctype.seva_subtype.seva_subtype.get_children",
	add_tree_node: "dhananjaya.dhananjaya.doctype.seva_subtype.seva_subtype.add_node",
	ignore_fields: ["parent_seva_subtype"],
	onload: function (treeview) {
		treeview.make_tree();
	},
}