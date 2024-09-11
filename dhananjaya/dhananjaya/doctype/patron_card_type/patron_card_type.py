# Copyright (c) 2024, Narahari Dasa and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class PatronCardType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		based_seva_type: DF.Check
		card_name: DF.Data
		threshold_amount: DF.Currency
	# end: auto-generated types
	pass
