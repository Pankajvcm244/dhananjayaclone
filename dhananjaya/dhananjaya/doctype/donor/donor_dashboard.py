from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        "heatmap": False,
        "fieldname": "donor",
        "transactions": [
            {"label": _("Links"), "items": ["Donation Receipt"]},
            {"label": _("Festival Benefits"), "items": ["Donor Festival Benefit"]},
            {"label": _("Reminders"), "items": ["DJ Reminder"]},
        ],
    }
