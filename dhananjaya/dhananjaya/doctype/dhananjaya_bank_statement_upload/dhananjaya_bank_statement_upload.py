# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.csvutils import get_csv_content_from_google_sheets, read_csv_content
from frappe.utils.xlsxutils import read_xls_file_from_attached_file, read_xlsx_file_from_attached_file
import datetime

class DhananjayaBankStatementUpload(Document):
	def get_data_from_template_file(self):
		content = None
		extension = None

		if self.google_sheets_link:
			content = get_csv_content_from_google_sheets(self.google_sheets_link)
			extension = "csv"

		if not content:
			frappe.throw(_("Invalid or corrupted content for import"))

		if not extension:
			extension = "csv"

		if content:
			return self.read_content(content, extension)
		
	def read_content(self, content, extension):
		error_title = _("Template Error")
		if extension not in ("csv", "xlsx", "xls"):
			frappe.throw(frappe._("Import template should be of type .csv, .xlsx or .xls"), title=error_title)

		if extension == "csv":
			data = read_csv_content(content)
		elif extension == "xlsx":
			data = read_xlsx_file_from_attached_file(fcontent=content)
		elif extension == "xls":
			data = read_xls_file_from_attached_file(content)

		return data

@frappe.whitelist()
def bank_statement_upload(*args,**kwargs):
	from frappe.utils.csvutils import read_csv_content
	upload_doc = frappe.get_cached_doc("Dhananjaya Bank Statement Upload")

	account_doc = frappe.get_doc("Bank Account",upload_doc.bank_account)
	
	rows = upload_doc.get_data_from_template_file()
	# count = 0
	# Get Index of Transaction ID
	headers = rows[0]

	# total_amount, total_fee = 0 ,0
	index = 1
	total = len(rows)
	check_bank_format(account_doc.bank, headers)
	for idx,row in enumerate(rows[1:]):
		data = {
			'doctype':'Bank Transaction',
			'bank_account': account_doc.name,
			'company': upload_doc.company,
			'status':'Unreconciled',
			# 'docstatus' : 1
			}
		if account_doc.bank == 'AU Small Finance Bank':
			if row[5] != "-" and row[4] != "-":
				break
			data['date'] = row[0]
			data['description'] = row[2]
			data['reference_number'] = row[3]
			data['withdrawal'] = row[4]
			data['deposit'] = row[5]
		
		elif account_doc.bank == 'Axis Bank':
			if row[4] is not None and row[5] is not None:
				break
			# if Date is None
			if row[1] is None:
				continue
			data['date'] = datetime.datetime.strptime(row[1], '%Y-%d-%m').strftime('%Y-%m-%d')
			# frappe.throw(f"Date {row[1]}")
			# data['date'] = row[1],
			data['description'] = row[3]
			data['withdrawal'] = row[4]
			data['deposit'] = row[5]
		
		elif account_doc.bank == 'ICICI Bank':
			# IF CR/DR Empty
			if row[6] is None:
				break
			if '-' in row[3]:
				data['date'] = datetime.datetime.strptime(row[3], '%d-%m-%Y %I:%M:%S %p').strftime('%Y-%m-%d')
			else:
				data['date'] = datetime.datetime.strptime(row[3], '%d/%m/%Y %I:%M:%S %p').strftime('%Y-%m-%d')
			data['description'] = row[5]
			if row[6] == 'CR':
				data['deposit'] = row[7]
			else:
				data['withdrawal'] = row[7]
			data['transaction_id'] = row[1]
		statement_doc = frappe.get_doc(data)
		statement_doc.save()
		statement_doc.submit()
		# frappe.show_progress('Loading..', index, total, 'Please wait')
	frappe.db.commit()
	return True

def check_bank_format(bank,headers):
	bank_formats = {
		"AU Small Finance Bank" : ['Trans Date','Value Date','Description/Narration','Chq./Ref.No.','Debit(Dr.) INR','Credit(Cr.) INR','Balance INR'],
		"Axis Bank" : ['SRL NO','Tran Date','CHQNO','PARTICULARS','DR','CR','BAL','SOL'],
		"ICICI Bank" : ['No.','Transaction ID','Value Date','Txn Posted Date','ChequeNo.','Description','Cr/Dr','Transaction Amount(INR)','Available Balance(INR)']
	}
	if not bank_formats[bank] == headers:
		frappe.throw("Bank Statement Format is not matching.")