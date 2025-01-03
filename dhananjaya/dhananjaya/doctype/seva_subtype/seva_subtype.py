# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from dhananjaya.dhananjaya.doctype.dhananjaya_notifier.dhananjaya_notifier import (
    generate_version,
)
from frappe.utils.nestedset import NestedSet

# from frappe.model.document import Document


class SevaSubtype(NestedSet):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from dhananjaya.dhananjaya.doctype.seva_subtype_defaults.seva_subtype_defaults import SevaSubtypeDefaults
        from dhananjaya.dhananjaya.doctype.yatra_seat_detail.yatra_seat_detail import YatraSeatDetail
        from frappe.types import DF

        amount: DF.Currency
        auto_cancel: DF.Int
        cost_centers: DF.Table[SevaSubtypeDefaults]
        enabled: DF.Check
        from_date: DF.Date | None
        include_in_analysis: DF.Check
        is_a_yatra: DF.Check
        is_group: DF.Check
        lft: DF.Int
        old_parent: DF.Link | None
        parent_seva_subtype: DF.Link | None
        patronship_allowed: DF.Check
        priority: DF.Int
        rgt: DF.Int
        seats: DF.Table[YatraSeatDetail]
        seva_name: DF.Data
        to_date: DF.Date | None
    # end: auto-generated types
    nsm_parent_field = "parent_seva_subtype"

    def on_change(self):
        generate_version(self.doctype)

    def on_update(self):
        super(SevaSubtype, self).on_update()
        self.delete_box_key()

    def on_trash(self):
        self.delete_box_key()

    def delete_box_key(self):
        frappe.cache().hdel("dhananjaya_box", "seva_subtype")

    def validate_from_to_dates(self, from_date_field: str, to_date_field: str) -> None:
        return super().validate_from_to_dates(from_date_field, to_date_field)

    def validate(self):
        self.validate_empty_seats()
        self.validate_duplicate()
        self.validate_from_to_dates("from_date", "to_date")


    def validate_empty_seats(self):
        seat = [i.seat_type for i in self.seats if i.count == 0]
        if seat:
            frappe.throw(f"Empty Seats Not Allowed")
    def validate_duplicate(self):
        seat = [i.seat_type for i in self.seats]
        duplicates = set([s for s in seat if seat.count(s) > 1])
        if duplicates:
            frappe.throw(f"Duplicates Entry Not Allowed")


@frappe.whitelist()
def get_cached_documents():
    seva_subtypes = (
        frappe.cache().hget("dhananjaya_box", "seva_subtype") or frappe._dict()
    )
    if not seva_subtypes:
        seva_subtypes = frappe.get_all(
            "Seva Subtype",
            fields=["*"],
            filters={"enabled": 1},
            order_by="priority desc",
        )
        frappe.cache().hset("dhananjaya_box", "seva_subtype", seva_subtypes)
    return seva_subtypes


@frappe.whitelist()
def get_children(doctype, parent, is_root=False):

    filters = [["enabled", "=", "1"]]

    if parent and not is_root:
        # via expand child
        filters.append(["parent_seva_subtype", "=", parent])
    else:
        filters.append(['ifnull(`parent_seva_subtype`, "")', "=", ""])

    types = frappe.get_list(
        doctype,
        fields=["name as value", "seva_name as title", "is_group as expandable"],
        filters=filters,
        order_by="name",
    )

    return types


@frappe.whitelist()
def add_node():
    from frappe.desk.treeview import make_tree_args

    args = frappe.form_dict
    args = make_tree_args(**args)

    if args.parent_seva_subtype == "All Types":
        args.parent_seva_subtype = None

    frappe.get_doc(args).insert()
