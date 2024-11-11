# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

from dhananjaya.dhananjaya.doctype.pg_upload_batch.pg_upload_batch import (
    refresh_pg_upload_batch,
)
import frappe
from frappe.model.document import Document


class PaymentGatewayTransaction(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        amount: DF.Currency
        batch: DF.Link | None
        company: DF.Link
        donor: DF.Link | None
        donor_name: DF.Data | None
        extra_data: DF.JSON | None
        fee: DF.Currency
        gateway: DF.Link
        receipt_created: DF.Check
        seva_type: DF.Link | None
        transaction_id: DF.Data
    # end: auto-generated types

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
