# Copyright (c) 2024, Narahari Dasa and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class APICity(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		city_name: DF.Data
		enabled: DF.Check
		state: DF.Link
	# end: auto-generated types
	pass
