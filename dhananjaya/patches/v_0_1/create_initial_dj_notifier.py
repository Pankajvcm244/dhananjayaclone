from frappe.desk.page.setup_wizard.setup_wizard import make_records


def execute():
    records = [
        {"doctype": "Dhananjaya Notifier", "doc_type": "DJ Mode of Payment"},
        {"doctype": "Dhananjaya Notifier", "doc_type": "Seva Type"},
        {"doctype": "Dhananjaya Notifier", "doc_type": "Seva Subtype"},
        {"doctype": "Dhananjaya Notifier", "doc_type": "DJ Payment Detail"},
    ]
    make_records(records)
