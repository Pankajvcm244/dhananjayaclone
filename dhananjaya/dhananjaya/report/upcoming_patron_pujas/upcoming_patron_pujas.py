# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

# import frappe

from datetime import datetime

from dhananjaya.dhananjaya.report.upcoming_patron_pujas.patron_puja_calculator import (
    get_patron_puja_dates,
)
from dhananjaya.dhananjaya.utils import get_preachers


def execute(filters=None):
    columns = get_columns()
    from_date = datetime.strptime(filters.get("from_date"), "%Y-%m-%d").date()
    to_date = datetime.strptime(filters.get("to_date"), "%Y-%m-%d").date()
    preachers = get_preachers()
    if filters.get("preacher"):
        if filters.get("preacher") in preachers:
            preachers = [filters.get("preacher")]
    upcoming_pujas = get_patron_puja_dates(from_date, to_date, preachers)
    return columns, upcoming_pujas


def get_columns():
    columns = [
        {
            "fieldname": "date",
            "label": "Date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "fieldname": "puja_id",
            "label": "Privilege Puja",
            "fieldtype": "Link",
            "options": "Patron Privilege Puja",
            "width": 150,
        },
        {
            "fieldname": "patron_id",
            "label": "Patron ID",
            "fieldtype": "Link",
            "options": "Patron",
            "width": 150,
        },
        {
            "fieldname": "patron_name",
            "label": "Full Name",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "fieldname": "occasion",
            "label": "Occasion",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "fieldname": "llp_preacher",
            "label": "Preacher",
            "fieldtype": "Data",
            "width": 120,
        },
    ]
    return columns
