# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class DonationCredit(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		company: DF.Link
		company_abbreviation: DF.Data | None
		credits: DF.Int
		donor: DF.Link
		donor_full_name: DF.Data | None
		kind_donation: DF.Check
		naming_series: DF.Literal[".company_abbreviation.-DC-.YY.-1.#####"]
		patron: DF.Link | None
		patron_name: DF.Data | None
		posting_date: DF.Date
		preacher: DF.Link
		remarks: DF.Data | None
		seva_subtype: DF.Link
	# end: auto-generated types
	pass
