# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from dhananjaya.dhananjaya.doctype.dhananjaya_notifier.dhananjaya_notifier import (
    generate_version,
)
from frappe.model.document import Document


class DJModeofPayment(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        description: DF.Data | None
        enabled: DF.Check
        kind: DF.Check
        mode: DF.Data | None
    # end: auto-generated types
    def on_change(self):
        generate_version(self.doctype)

    def on_update(self):
        self.delete_box_key()

    def on_trash(self):
        self.delete_box_key()

    def delete_box_key(self):
        frappe.cache().hdel("dhananjaya_box", "dj_mode_of_payment")


@frappe.whitelist()
def get_cached_documents():
    payment_modes = (
        frappe.cache().hget("dhananjaya_box", "dj_mode_of_payment") or frappe._dict()
    )
    if not payment_modes:
        payment_modes = frappe.get_all(
            "DJ Mode of Payment", fields=["*"], filters={"enabled": 1}
        )
        frappe.cache().hset("dhananjaya_box", "dj_mode_of_payment", payment_modes)
    return payment_modes
