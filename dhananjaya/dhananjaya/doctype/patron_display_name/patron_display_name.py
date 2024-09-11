# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class PatronDisplayName(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		full_name: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		type: DF.Literal["Company", "Person"]
	# end: auto-generated types
	pass
