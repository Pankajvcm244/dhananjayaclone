# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import json
from dhananjaya.dhananjaya.utils import get_company_defaults
import frappe
from frappe.model.document import Document
from rapidfuzz import process, fuzz


class PGUploadBatch(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        bank_account: DF.Link | None
        bank_amount: DF.Currency
        bank_transaction: DF.Link | None
        batch_amount: DF.Currency
        company: DF.Link
        gateway: DF.Link
        gateway_expense_account: DF.Link | None
        name: DF.Int | None
        remaining_amount: DF.Currency
        resolved_amount: DF.Currency
        resolved_fee: DF.Currency
        status: DF.Literal["Open", "Closed"]
        total_amount: DF.Currency
        total_fee: DF.Currency

    # end: auto-generated types
    def before_insert(self):
        # set default donation account
        company_detail = get_company_defaults(self.company)
        self.gateway_expense_account = company_detail.gateway_expense_account

    # def on_change(self):
    #     self.set_status()

    # def set_status(self):
    # if self.remaining_amount == 0 and self.status == "Open":
    # self.db_set("status", "Closed")


def refresh_pg_upload_batch(name):
    batch_doc = frappe.get_doc("PG Upload Batch", name)
    total_amount = 0
    total_fee = 0
    resolved_amount = 0
    resolved_fee = 0
    bank_amount = 0
    for tx in frappe.get_all(
        "Payment Gateway Transaction",
        filters={"batch": name},
        fields=["name", "amount", "fee", "receipt_created"],
    ):
        total_amount += tx["amount"]
        total_fee += tx["fee"]
        if tx["receipt_created"]:
            resolved_amount += tx["amount"]
            resolved_fee += tx["fee"]
    if batch_doc.bank_transaction:
        bank_amount = frappe.get_value(
            "Bank Transaction", batch_doc.bank_transaction, "unallocated_amount"
        )
    remaining_amount = (total_amount - total_fee) - (resolved_amount - resolved_fee)
    frappe.db.set_value(
        "PG Upload Batch",
        name,
        {
            "total_amount": total_amount,
            "total_fee": total_fee,
            "batch_amount": total_amount - total_fee,
            "resolved_amount": resolved_amount,
            "resolved_fee": resolved_fee,
            "remaining_amount": remaining_amount,
            "bank_amount": bank_amount,
            "status": "Closed" if remaining_amount == 0 else "Open",
        },
        update_modified=False,
    )


@frappe.whitelist()
def count_donor_linked(batch):
    total, resolved, unresolved_donor_linked = 0, 0, 0
    for tx in frappe.db.get_all(
        "Payment Gateway Transaction",
        filters={"batch": batch},
        fields=["donor", "receipt_created"],
    ):
        if tx["receipt_created"]:
            resolved += 1
        elif tx["donor"]:
            unresolved_donor_linked += 1
        total += 1
    return total, resolved, unresolved_donor_linked


@frappe.whitelist()
def get_payment_entries(batch):
    txs = frappe.db.get_all(
        "Payment Gateway Transaction", filters={"batch": batch}, pluck="name"
    )
    return txs


@frappe.whitelist()
def set_seva_type_bulk(batch, seva_type):
    frappe.db.sql(
        f"""
					update `tabPayment Gateway Transaction`
					set seva_type = '{seva_type}'
					where batch = '{batch}' AND receipt_created = 0
					"""
    )
    frappe.db.commit()


@frappe.whitelist()
def disconnect_cancelled_receipts(batch):
    frappe.db.sql(
        f"""
            UPDATE `tabDonation Receipt` tdr
            JOIN `tabPayment Gateway Transaction` tpgt
            ON tdr.payment_gateway_document = tpgt.name
            JOIN `tabPG Upload Batch` tpb
            ON tpb.name = tpgt.batch
            SET payment_gateway_document = NULL
            WHERE tpb.name = '{batch}' AND tdr.docstatus = 2
		"""
    )
    frappe.db.commit()
