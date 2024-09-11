import json
import unittest

import frappe

from dhananjaya.dhananjaya.api.v3.marketing.main import upload_donation


class TestEvent(unittest.TestCase):
	def test_fields_missing(self):
		self.assertRaises(Exception,create_receipt(FIELD_MISSING_DICT))
	
	def test_fields_atg_required(self): 
		self.assertRaises(Exception,create_receipt(ATG_REQUIRED_MISSING_DICT))



def create_receipt(
	donation:dict
):
	donation = json.dumps(donation)
	frappe.request = frappe._dict(data = donation)
	return upload_donation()


FIELD_MISSING_DICT = {
				"donation": {
					"donor_name":"Naresh Jangid",
					"preacher":"NRHD",
					"pan_no":"AAAAA1235P",
					"payment_method":"Gateway",
					"mobile":"7357010770",
					"address":"Bikaner,Rajasthan - 324007",
					"company":"Shubhodaya Foundation",
					"amount":1000,
					"date":"2023-10-29",
					"remarks":"remakrs here",
					"seva_type":"General Donation - SF"
				}
			}

ATG_REQUIRED_MISSING_DICT = {
				"donation": {
					"donor_name":"Naresh Jangid",
					"preacher":"NRHD",
					"payment_method":"Gateway",
					"mobile":"7357010770",
					"address":"Bikaner,Rajasthan - 324007",
					"company":"Shubhodaya Foundation",
					"amount":1000,
					"date":"2023-10-29",
					"remarks":"remakrs here",
					"seva_type":"General Donation - SF",
					"atg_required":True
				}
			}