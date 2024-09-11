# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class PatronCardDetail(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		card_type: DF.Link | None
		number: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		serial: DF.Data | None
		valid_from: DF.Date | None
	# end: auto-generated types
	pass
