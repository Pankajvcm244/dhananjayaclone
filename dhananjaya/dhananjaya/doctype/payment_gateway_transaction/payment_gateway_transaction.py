# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

from dhananjaya.dhananjaya.doctype.pg_upload_batch.pg_upload_batch import (
    refresh_pg_upload_batch,
)
import frappe
from frappe.model.document import Document


class PaymentGatewayTransaction(Document):

    def on_update(self):
        self.update_donor_receipt_matching_transaction()
        refresh_pg_upload_batch(self.batch)

    def update_donor_receipt_matching_transaction(self):
        for receipt in frappe.db.get_all(
            "Donation Receipt",
            filters={"payment_gateway_document": self.name},
            fields=["name", "donor"],
        ):
            if receipt["donor"]:
                continue
            frappe.db.set_value(
                "Donation Receipt",
                receipt["name"],
                {"donor": self.donor, "full_name": self.donor_name},
            )

    def on_trash(self):
        refresh_pg_upload_batch(self.batch)
