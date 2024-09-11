# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class PatronGiftIssue(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		gift: DF.Link | None
		issued_on: DF.Date | None
		language: DF.Literal["English", "Hindi", "Bengali", "Marathi", "Gujarati", "Punjabi", "KashmiriAssamese"]
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types
	pass
