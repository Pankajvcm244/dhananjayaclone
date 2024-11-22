# Copyright (c) 2024, Narahari Dasa and contributors
# For license information, please see license.txt

from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_dimensions
import frappe
from datetime import datetime, timedelta
from frappe.query_builder import DocType


def execute(filters=None):

	dimensions = filters.get("dimension")
	dimension_list = get_dimensions()[0]
	weeks = calculate_weeks(filters.get("from_date"), filters.get("to_date"))
	column = get_columns(filters ,weeks , dimension_list , dimensions)
	data = get_data(filters, weeks , dimension_list , dimensions)
	return column, data


def get_columns(filters ,weeks , dimension_list , dimensions):
    
	 
	field_name = None
	label = None
	for d in dimension_list:
		if d.get("label") == dimensions:
			field_name = d.get("fieldname")
			label = d.get("label")

	columns = []
	
	if dimensions == "Project":
		columns = [
			{
				"fieldname": "project",
				"label": "<b>Project</b>",
				"fieldtype": "Data",
				"width": 300,
			}
			
		]
  
	elif dimensions == "Cost Center":
		columns = [
			{
				"fieldname": "cost_center",
				"label": "<b>Cost Center</b>",
				"fieldtype": "Data",
				"width": 300,
			}
			
		]
	else:
		columns = [
        	{
			"fieldname": f"{field_name}",
            "label": f"<b>{label}</b>",
            "fieldtype": "Data",
            "width": 120,
       		 }
	] 
	 
	for idx , week in enumerate(weeks , 1):
		columns.append(
            {
                "fieldname": f"week{idx}",
                "label":f"<b> Week {idx} </b>",
                "fieldtype": "Data",
                "width": 120,
            }
        )
	columns.append(
        {
            "fieldname": "total",
            "label": "<b>Total</b>",
            "fieldtype": "Data",
            "width": 120,
        }
    )
	
	return columns


def get_data(filters, weeks , dimension_list , dimensions):

	data = []
 
	if dimensions == "Project":
			data = []
			entries = frappe.db.sql(
				f"""
					SELECT
						DATE(dr.receipt_date) AS receipt_date,
						p.project_name AS project,
						dr.name , 
						dr.amount
					FROM `tabDonation Receipt` dr
					LEFT JOIN `tabProject` p 
						ON p.name = dr.project
					LEFT JOIN `tabLLP Preacher` preacher 
						ON preacher.name = dr.preacher
					LEFT JOIN `tabSeva Type` st 
						ON st.name = dr.seva_type
					LEFT JOIN `tabSeva Subtype` sst 
						ON sst.name = dr.seva_subtype
					WHERE dr.workflow_state = 'Realized'
						AND preacher.include_in_analysis = 1
						AND st.include_in_analysis = 1
						AND sst.include_in_analysis = 1
						AND dr.receipt_date BETWEEN '{filters.get("from_date")}' AND '{filters.get("to_date")}'
						AND dr.project IS NOT NULL
					ORDER BY dr.receipt_date
				"""
			, as_dict=1)
			project = {}
			for entry in entries:
				if entry["project"] not in project:
					project.setdefault(
						entry["project"],
						{
						"project": entry["project"],  
						"total": 0  
						}
						)
					for idx , week in enumerate(weeks , 1):
						project[entry["project"]].setdefault(f"week{idx}", 0)
				for idx , week in enumerate(weeks , 1):
					if entry["receipt_date"] >= week[0] and entry["receipt_date"] <= week[1]:
						project[entry["project"]][f"week{idx}"] += entry["amount"]
						break
				project[entry["project"]]["total"] += entry["amount"]		
			data = list(project.values())
			return data
	if dimensions == "Cost Center":
			data = []
			entries = frappe.db.sql(
				f"""
					SELECT
						DATE(dr.receipt_date) AS receipt_date,
						cc.name AS cost_center,
						dr.name , 
						dr.amount
					FROM `tabDonation Receipt` dr
					LEFT JOIN `tabCost Center` cc 
						ON cc.name = dr.cost_center
					LEFT JOIN `tabLLP Preacher` preacher 
						ON preacher.name = dr.preacher
					LEFT JOIN `tabSeva Type` st 
						ON st.name = dr.seva_type
					LEFT JOIN `tabSeva Subtype` sst 
						ON sst.name = dr.seva_subtype
					WHERE dr.workflow_state = 'Realized'
						AND preacher.include_in_analysis = 1
						AND st.include_in_analysis = 1
						AND sst.include_in_analysis = 1
						AND dr.receipt_date BETWEEN '{filters.get("from_date")}' AND '{filters.get("to_date")}'
						AND dr.cost_center IS NOT NULL
					ORDER BY dr.receipt_date
				"""
			, as_dict=1)
			cost_center = {}
			for entry in entries:
				if entry["cost_center"] not in cost_center:
					cost_center.setdefault(
						entry["cost_center"],
						{
						"cost_center": entry["cost_center"],  
						"total": 0  
						}
						)
					for idx , week in enumerate(weeks , 1):
						cost_center[entry["cost_center"]].setdefault(f"week{idx}", 0)
				for idx , week in enumerate(weeks , 1):
					if entry["receipt_date"] >= week[0] and entry["receipt_date"] <= week[1]:
						cost_center[entry["cost_center"]][f"week{idx}"] += entry["amount"]
						break
				cost_center[entry["cost_center"]]["total"] += entry["amount"]		
			data = list(cost_center.values())
			return data
	field_name = None
	document_type = None
	label = None
	for d in dimension_list:
		if d.get("label") == dimensions:
			field_name = d.get("fieldname")
			document_type = d.get("document_type")
			label = d.get("label")
   
	title_field = frappe.get_meta(document_type).get_title_field()

	entries = frappe.db.sql(
				f"""
					SELECT
						DATE(dr.receipt_date) AS receipt_date,
						d.name AS dimension,
						d.{title_field} AS dimension_name,
						dr.name , 
						dr.amount
					FROM `tabDonation Receipt` dr
					LEFT JOIN `tab{document_type}` d 
						ON d.name = dr.{field_name}
					LEFT JOIN `tabLLP Preacher` preacher 
						ON preacher.name = dr.preacher
					LEFT JOIN `tabSeva Type` st 
						ON st.name = dr.seva_type
					LEFT JOIN `tabSeva Subtype` sst 
						ON sst.name = dr.seva_subtype
					WHERE dr.workflow_state = 'Realized'
						AND preacher.include_in_analysis = 1
						AND st.include_in_analysis = 1
						AND sst.include_in_analysis = 1
						AND dr.receipt_date BETWEEN '{filters.get("from_date")}' AND '{filters.get("to_date")}'
						AND dr.{field_name} IS NOT NULL
					ORDER BY dr.receipt_date
				"""
			, as_dict=1)
	dimension_data = {}
	for entry in entries:
				if entry["dimension"] not in dimension_data:
					
					
					dimension_data.setdefault(
						entry["dimension"],
						{
						f"{field_name}": entry["dimension_name"],  
						"total": 0  
						}
						)
					for idx , week in enumerate(weeks , 1):
						dimension_data[entry["dimension"]].setdefault(f"week{idx}", 0)
				for idx , week in enumerate(weeks , 1):
					if entry["receipt_date"] >= week[0] and entry["receipt_date"] <= week[1]:
						project[entry["dimension"]][f"week{idx}"] += entry["amount"]
						break
				dimension_data[entry["dimension"]]["total"] += entry["amount"]		
	data = list(dimension_data.values())				
	return  data    
        	


def calculate_weeks(from_date, to_date):
    start_date = datetime.strptime(from_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(to_date, "%Y-%m-%d").date()

 
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    weeks = []
    current_start = start_date

    while current_start <= end_date:
        current_end = current_start + timedelta(days=(6 - current_start.weekday()))
        if current_end > end_date:
            current_end = end_date 
        weeks.append((current_start, current_end))
        current_start = current_end + timedelta(days=1)  # Start of the next week

    return weeks

