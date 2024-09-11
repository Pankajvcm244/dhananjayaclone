# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class DhananjayaSettingsCompanyDetails(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		atg_lines: DF.HTMLEditor | None
		authority_name: DF.Data | None
		authority_position: DF.Data | None
		authority_signature: DF.AttachImage | None
		auto_create_journal_entries: DF.Check
		bank_account: DF.Link | None
		cash_account: DF.Link
		company: DF.Link
		company_tagline: DF.Data | None
		contact_address: DF.Data | None
		contact_email: DF.Data | None
		contact_no: DF.Data | None
		credit_value: DF.Int
		donation_account: DF.Link
		gateway_expense_account: DF.Link | None
		logo: DF.AttachImage | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		preacher_allowed_receipt_creation: DF.Check
		seal: DF.AttachImage | None
		thanks_note: DF.HTMLEditor | None
	# end: auto-generated types
	pass
