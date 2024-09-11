# Copyright (c) 2024, Narahari Dasa and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SevaSubtypeCostCenter(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		company: DF.Link
		cost_center: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types
	pass
