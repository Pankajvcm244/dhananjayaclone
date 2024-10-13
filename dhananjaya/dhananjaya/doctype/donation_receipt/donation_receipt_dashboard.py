from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        "heatmap": False,
        "fieldname": "donation_receipt",
        "non_standard_fieldnames": {"Bank Transaction": "payment_entry"},
        "transactions": [
            {
                "label": _("References"),
                "items": ["Journal Entry", "Bank Transaction", "Asset"],
            },
            {"label": _("Festival Benefits"), "items": ["Donor Festival Benefit"]},
        ],
    }
