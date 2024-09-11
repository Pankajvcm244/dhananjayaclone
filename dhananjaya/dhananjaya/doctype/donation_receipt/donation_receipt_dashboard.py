from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        "heatmap": False,
        "fieldname": "donation_receipt",
        "transactions": [
            {"label": _("References"), "items": ["Journal Entry"]},
            {"label": _("Festival Benefits"), "items": ["Donor Festival Benefit"]},
        ],
    }
