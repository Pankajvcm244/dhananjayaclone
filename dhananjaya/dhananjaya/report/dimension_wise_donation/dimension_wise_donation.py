# Copyright (c) 2024, Narahari Dasa and contributors
# For license information, please see license.txt

from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
    get_dimensions,
)
import frappe
from datetime import datetime, timedelta
from frappe.query_builder import DocType


def execute(filters=None):

    dimensions = filters.get("dimension")
    dimension_list = get_dimensions()[0]
    weeks = calculate_weeks(filters.get("from_date"), filters.get("to_date"))
    column = get_columns(filters, weeks, dimension_list, dimensions)
    data = get_data(filters, weeks, dimension_list, dimensions)
    return column, data


def get_columns(filters, weeks, dimension_list, dimensions):

    field_name = None
    label = None
    document_type = None
    for d in dimension_list:
        if d.get("label") == dimensions:
            field_name = d.get("fieldname")
            label = d.get("label")
            document_type = d.get("document_type")

    columns = []

    if dimensions == "Project":
        columns = [
            {
                "fieldname": "weeks",
                "label": "<b>Weeks</b>",
                "fieldtype": "Data",
                "width": 100,
            }
        ]

        columns.extend(
            [
                {
                    "fieldname": p.lower(),
                    "label": f"<b>{p.capitalize()}</b>",
                    "fieldtype": "Currency",
                    "width": 150,
                }
                for p in frappe.get_all("Project", pluck="project_name")
            ]
        )

    elif dimensions == "Cost Center":
        columns = [
            {
                "fieldname": "weeks",
                "label": "<b>Weeks</b>",
                "fieldtype": "Data",
                "width": 100,
            }
        ]
        columns.extend(
            [
                {
                    "fieldname": p,
                    "label": f"<b>{p}</b>",
                    "fieldtype": "Currency",
                    "width": 150,
                }
                for p in frappe.get_all("Cost Center", pluck="name")
            ]
        )

    else:
        columns = [
            {
                "fieldname": "weeks",
                "label": "<b>Weeks</b>",
                "fieldtype": "Data",
                "width": 100,
            }
        ]
        title_field = frappe.get_meta(document_type).get_title_field() or "name"

        columns.extend(
            [
                {
                    "fieldname": p,
                    "label": f"<b>{p}</b>",
                    "fieldtype": "Currency",
                    "width": 150,
                }
                for p in frappe.get_all(document_type, pluck=title_field)
            ]
        )

    return columns


def get_data(filters, weeks, dimension_list, dimensions):

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
				""",
            as_dict=1,
        )
        project = {}

        projects_list = frappe.get_all("Project", pluck="project_name")
        for idx, week in enumerate(weeks, 1):
            project[f"weeks{idx}"] = {
                "weeks": f"Week {idx}",
                **{p.lower(): 0 for p in projects_list},
            }
        project_grand_total = {p.lower(): 0 for p in projects_list}

        for entry in entries:
            for idx, week in enumerate(weeks, 1):
                if (
                    entry["receipt_date"] >= week[0]
                    and entry["receipt_date"] <= week[1]
                ):
                    project[f"weeks{idx}"][entry["project"].lower()] += entry["amount"]

                    break

            project_grand_total[entry["project"].lower()] += entry["amount"]

        data = list(project.values())
        empty_row_count = 2  # Number of empty rows to add
        for _ in range(empty_row_count):
            data.append({"weeks": "", **{p.lower(): None for p in projects_list}})
        data.append(
            {
                "weeks": "<Strong>Grand Total </Strong>",
                **{key: value for key, value in project_grand_total.items()},
            }
        )
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
				""",
            as_dict=1,
        )
        cost_center = {}
        cost_center_list = frappe.get_all("Cost Center", pluck="name")
        for idx, week in enumerate(weeks, 1):
            cost_center[f"weeks{idx}"] = {
                "weeks": f"Week {idx}",
                **{p: 0 for p in cost_center_list},
            }
        cost_center_grand_total = {p: 0 for p in cost_center_list}
        for entry in entries:
            for idx, week in enumerate(weeks, 1):
                if (
                    entry["receipt_date"] >= week[0]
                    and entry["receipt_date"] <= week[1]
                ):
                    cost_center[f"weeks{idx}"][entry["cost_center"]] += entry["amount"]

                    break

            cost_center_grand_total[entry["cost_center"]] += entry["amount"]
        data = list(cost_center.values())
        empty_row_count = 2  # Number of empty rows to add
        for _ in range(empty_row_count):
            data.append({"weeks": "", **{p: None for p in cost_center_list}})
        data.append(
            {
                "weeks": "<h4>Grand Total </h4>",
                **{key: value for key, value in cost_center_grand_total.items()},
            }
        )
        return data

    field_name = None
    document_type = None
    label = None
    for d in dimension_list:
        if d.get("label") == dimensions:
            field_name = d.get("fieldname")
            document_type = d.get("document_type")
            label = d.get("label")

    title_field = frappe.get_meta(document_type).get_title_field() or "name"

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
					WHERE preacher.include_in_analysis = 1
						AND st.include_in_analysis = 1
						AND sst.include_in_analysis = 1
						AND dr.receipt_date BETWEEN '{filters.get("from_date")}' AND '{filters.get("to_date")}'
						AND dr.{field_name} IS NOT NULL
					ORDER BY dr.receipt_date
				""",
        as_dict=1,
    )

    dimension_data = {}
    dimension_data_list = frappe.get_all(document_type, pluck=title_field)
    for idx, week in enumerate(weeks, 1):
        dimension_data[f"weeks{idx}"] = {
            "weeks": f"Week {idx}",
            **{p: 0 for p in dimension_data_list},
        }
    dimension_data_grand_total = {p: 0 for p in dimension_data_list}
    for entry in entries:
        for idx, week in enumerate(weeks, 1):
            if entry["receipt_date"] >= week[0] and entry["receipt_date"] <= week[1]:
                dimension_data[f"weeks{idx}"][entry["dimension_name"]] += entry[
                    "amount"
                ]

                break

        dimension_data_grand_total[entry["dimension_name"]] += entry["amount"]

    data = list(dimension_data.values())

    empty_row_count = 2
    for _ in range(empty_row_count):
        data.append({"weeks": "", **{p: None for p in dimension_data_list}})
    data.append(
        {
            "weeks": "<Strong>Grand Total </Strong>",
            **{key: value for key, value in dimension_data_grand_total.items()},
        }
    )
    return data


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
