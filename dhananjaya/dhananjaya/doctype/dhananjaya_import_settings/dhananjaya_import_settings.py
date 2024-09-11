# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt


from frappe.model.document import Document

class DhananjayaImportSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from dhananjaya.dhananjaya.doctype.dhananjaya_import_settings_company.dhananjaya_import_settings_company import DhananjayaImportSettingsCompany
		from frappe.types import DF

		companies_to_import: DF.Table[DhananjayaImportSettingsCompany]
		database_name: DF.Data | None
		defective_patrons: DF.Int
		host: DF.Data | None
		is_a_test: DF.Check
		mysql_password: DF.Data | None
		mysql_user: DF.Data | None
		patron_correction_template_file: DF.Attach | None
		test_run_records: DF.Int
		upload_merge_file: DF.Attach | None
	# end: auto-generated types
	pass