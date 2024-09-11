# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

from datetime import datetime
from dhananjaya.dhananjaya.report.upcoming_special_pujas.puja_calculator import (
    get_puja_dates,
)

def execute(filters=None):
    columns = get_columns()
    from_date = datetime.strptime(filters.get("from_date"), "%Y-%m-%d").date()
    to_date = datetime.strptime(filters.get("to_date"), "%Y-%m-%d").date()
    preacher = []
    if filters.get("preacher"):
        preacher = [filters.get("preacher")]
    upcoming_pujas = get_puja_dates(from_date, to_date, preacher)
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
            "fieldname": "donor_id",
            "label": "Donor ID",
            "fieldtype": "Link",
            "options": "Donor",
            "width": 120,
        },
        {
            "fieldname": "donor_name",
            "label": "Full Name",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "fieldname": "occasion",
            "label": "Occasion",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "fieldname": "llp_preacher",
            "label": "Preacher",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "fieldname": "total_donation",
            "label": "Total Donation",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "fieldname": "last_donation",
            "label": "Last Donation",
            "fieldtype": "Currency",
            "width": 120,
        },
    ]
    return columns
