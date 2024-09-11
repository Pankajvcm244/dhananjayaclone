from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        "heatmap": False,
        "fieldname": "seva_type",
        "non_standard_fieldnames": {
            "Donation Receipt": "seva_type",
        },
        "transactions": [{"label": _("Links"), "items": ["Donation Receipt"]}],
    }
