# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class DonorAddress(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		address_line_1: DF.Data
		address_line_2: DF.Data | None
		city: DF.Data | None
		country: DF.Data | None
		latitude: DF.Float
		longitude: DF.Float
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		pin_code: DF.Data | None
		preferred: DF.Check
		state: DF.Data | None
		type: DF.Literal["Residential", "Office", "Other", "Factory"]
	# end: auto-generated types
	pass
