# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

PREACHER_ROLE = "DCC Preacher"


class LLPPreacher(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from dhananjaya.dhananjaya.doctype.llp_preacher_user.llp_preacher_user import (
            LLPPreacherUser,
        )
        from frappe.types import DF

        allowed_users: DF.Table[LLPPreacherUser]
        full_name: DF.Data
        include_in_analysis: DF.Check
        initial: DF.Data
        mobile_no: DF.Data | None

    # end: auto-generated types
    def on_update(self):
        for user_row in self.allowed_users:
            if PREACHER_ROLE not in frappe.get_roles(user_row.user):
                user = frappe.get_doc("User", user_row.user)
                user.add_roles([PREACHER_ROLE])

    # def after_insert(self):
    #     self.create_devotee_dimension()

    # def create_devotee_dimension(self):
    #     if frappe.db.exists("DocType", {"name": "Devotee"}):
    #         if not frappe.db.exists("Devotee", self.name):
    #             frappe.get_doc({"doctype": "Devotee", "name1": self.name}).insert()
    #     return
