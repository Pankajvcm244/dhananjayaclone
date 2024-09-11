from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        "heatmap": False,
        "fieldname": "patron_seva_type",
        "non_standard_fieldnames": {
            "Patron": "seva_type",
        },
        "transactions": [{"label": _("Links"), "items": ["Patron"]}],
    }
