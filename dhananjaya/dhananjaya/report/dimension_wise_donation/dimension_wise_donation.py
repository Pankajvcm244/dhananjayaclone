# Copyright (c) 2024, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime, timedelta
from frappe.query_builder import DocType


def execute(filters=None):
	print(type(filters.get("from_date")))
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	weeks = calculate_weeks(from_date, to_date)
	column = get_columns(weeks)
	data = get_data(filters, weeks)
	frappe.errprint(column)
	return column, data


def get_columns(weeks):
    columns = [
        {
            "fieldname": "project",
            "label": "Project",
            "fieldtype": "data",
            "width": 120,
        }
    ]
    for idx , week in enumerate(weeks):
        columns.append(
            {
                "fieldname": f"week{idx}",
                "label": week[0].strftime("%d/%m/%Y")
                + " to "
                + week[1].strftime("%d/%m/%Y"),
                "fieldtype": "Data",
                "width": 120,
            }
        )
    columns.append(
        {
            "fieldname": "total",
            "label": "Total",
            "fieldtype": "Data",
            "width": 120,
        }
    )
	
    return columns


def get_data(filters, weeks):

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
			for idx , week in enumerate(weeks):
				project[entry["project"]].setdefault(f"week{idx}", 0)
		for idx , week in enumerate(weeks):
			if entry["receipt_date"] >= week[0] and entry["receipt_date"] <= week[1]:
				project[entry["project"]][f"week{idx}"] += entry["amount"]
				break
		project[entry["project"]]["total"] += entry["amount"]		
	data = list(project.values())
             
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

