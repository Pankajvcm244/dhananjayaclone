# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.model.document import Document

class DonorMerger(Document):
	pass

@frappe.whitelist()
def get_donor_details(donor):
	data = frappe.get_doc("Donor",donor)
	return data.as_json()

clean_fields = ['name','creation','modified','modified_by','owner', 'docstatus','idx','parent','parenttype','parentfield']

def clean_child_doc(doc_json):
	for f in clean_fields:
		doc_json.pop(f)
	return doc_json

def clean_addresses(donor,addresses):
	# redesign_addresses_keeping_first_preferred
	found_preferred = False
	for d in addresses:
		if d.get("preferred") == 1 and not found_preferred:
			found_preferred = True
		else:
			d["preferred"] = 0
		# Remove unnecessary fields as we will add them fresh to the Primary Donor.
		d = clean_child_doc(d)
	return addresses

def clean_contacts(donor,contacts):
	contacts = [c['contact_no'] for c in contacts]
	cleaned_contacts = []
	for c in contacts:
		if c not in cleaned_contacts:
			cleaned_contacts.append(c)
	return [frappe._dict(contact_no = c) for c in cleaned_contacts]

@frappe.whitelist()
def merge_donors(donor_first, donor_second, priority_first,	priority_second, address_values,contact_values):
	priority_first = int(priority_first)
	priority_second = int(priority_second)
	address_values = json.loads(address_values)
	contact_values = json.loads(contact_values)

	if priority_first:
		merge_to = frappe.get_doc("Donor",donor_first)
		merge_from = frappe.get_doc("Donor",donor_second)
	elif priority_second:
		merge_to = frappe.get_doc("Donor",donor_second)
		merge_from = frappe.get_doc("Donor",donor_first)
	
	# chosen_addresses = []

	chosen_addresses = frappe.get_all("Donor Address", filters = {"name":["IN",address_values]}, fields = '*')

	chosen_addresses = clean_addresses(merge_to,chosen_addresses)
	
	chosen_contacts = frappe.get_all("Donor Contact", filters = {"name":["IN",contact_values]}, fields = '*')

	chosen_contacts = clean_contacts(merge_to,chosen_contacts)

	meta = frappe.get_meta("Donor")

	ignore_fields = ["addresses","contacts"]

	## In Child Tables, give a field to check Duplicate entries.
	child_duplicate_field_map = {
		"emails":"email"
	}

	for field in meta.fields:
		if field.fieldname in ignore_fields:
			continue
		
		to_field_value = getattr(merge_to, field.fieldname, None)
		from_field_value = getattr(merge_from, field.fieldname, None)

		if field.fieldtype == "Table" and from_field_value and len(from_field_value)>0:
			all_children = to_field_value
			duplicate_check_field = child_duplicate_field_map.get(field.fieldname,None)
			for child in from_field_value:
				child = clean_child_doc(child.as_dict())
				if duplicate_check_field:
					exists = any(ch.get(duplicate_check_field) == child.get(duplicate_check_field) for ch in all_children)
					if not exists:
						all_children.append(child)
				else:
					all_children.append(child)
			setattr(merge_to, field.fieldname, [])
			merge_to.extend(field.fieldname,all_children)
			continue
	
		if from_field_value and not to_field_value:
			if field.unique:
				setattr(merge_from, field.fieldname, None)
			setattr(merge_to, field.fieldname, from_field_value)

	merge_to.addresses = []
	merge_to.contacts =  []
	
	merge_to.extend("addresses",chosen_addresses)
	merge_to.extend("contacts",chosen_contacts)

	merge_from.save()
	merge_to.save()
	frappe.db.commit()
	frappe.rename_doc("Donor", merge_from.name, merge_to.name, merge=1)
	return