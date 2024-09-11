from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        "heatmap": False,
        "fieldname": "patron",
        "non_standard_fieldnames": {
            "Donation Receipt": "patron",
        },
        "transactions": [
            {"label": _("Links"), "items": ["Donation Receipt", "Patron Privilege Puja", "Donation Credit"]}
        ],
    }
