from frappe.desk.page.setup_wizard.setup_wizard import make_records
import frappe


COMPANY_PERMS = [
    {
        "role": "DCC Preacher",
        "parent": "Company",
        "permlevel": 0,
        "read": 1,
        "print": 1,
        "report": 1,
        "share": 1,
        "parentfield": "permissions",
        "parenttype": "DocType",
        "doctype": "Custom DocPerm",
    },
    {
        "role": "DCC Executive",
        "parent": "Company",
        "permlevel": 0,
        "read": 1,
        "print": 1,
        "report": 1,
        "share": 1,
        "parentfield": "permissions",
        "parenttype": "DocType",
        "doctype": "Custom DocPerm",
    },
    {
        "role": "DCC Manager",
        "parent": "Company",
        "permlevel": 0,
        "read": 1,
        "print": 1,
        "report": 1,
        "share": 1,
        "parentfield": "permissions",
        "parenttype": "DocType",
        "doctype": "Custom DocPerm",
    },
    {
        "role": "DCC Cashier",
        "parent": "Company",
        "permlevel": 0,
        "read": 1,
        "print": 1,
        "report": 1,
        "share": 1,
        "parentfield": "permissions",
        "parenttype": "DocType",
        "doctype": "Custom DocPerm",
    },
]

WORKFLOW_STATE_PERMS = [
    {
        "role": "DCC Preacher",
        "parent": "Workflow State",
        "permlevel": 0,
        "read": 1,
        "print": 1,
        "report": 1,
        "share": 1,
        "parentfield": "permissions",
        "parenttype": "DocType",
        "doctype": "Custom DocPerm",
    },
    {
        "role": "DCC Executive",
        "parent": "Workflow State",
        "permlevel": 0,
        "read": 1,
        "print": 1,
        "report": 1,
        "share": 1,
        "parentfield": "permissions",
        "parenttype": "DocType",
        "doctype": "Custom DocPerm",
    },
    {
        "role": "DCC Manager",
        "parent": "Workflow State",
        "permlevel": 0,
        "read": 1,
        "print": 1,
        "report": 1,
        "share": 1,
        "parentfield": "permissions",
        "parenttype": "DocType",
        "doctype": "Custom DocPerm",
    },
    {
        "role": "DCC Cashier",
        "parent": "Workflow State",
        "permlevel": 0,
        "read": 1,
        "print": 1,
        "report": 1,
        "share": 1,
        "parentfield": "permissions",
        "parenttype": "DocType",
        "doctype": "Custom DocPerm",
    },
]

BANK_ACCOUNT_PERMS = [
    {
        "role": "DCC Preacher",
        "parent": "Bank Account",
        "permlevel": 0,
        "read": 1,
        "print": 1,
        "report": 1,
        "share": 1,
        "parentfield": "permissions",
        "parenttype": "DocType",
        "doctype": "Custom DocPerm",
    },
    {
        "role": "DCC Executive",
        "parent": "Bank Account",
        "permlevel": 0,
        "read": 1,
        "print": 1,
        "report": 1,
        "share": 1,
        "parentfield": "permissions",
        "parenttype": "DocType",
        "doctype": "Custom DocPerm",
    },
    {
        "role": "DCC Manager",
        "parent": "Bank Account",
        "permlevel": 0,
        "read": 1,
        "print": 1,
        "report": 1,
        "share": 1,
        "parentfield": "permissions",
        "parenttype": "DocType",
        "doctype": "Custom DocPerm",
    },
    {
        "role": "DCC Cashier",
        "parent": "Bank Account",
        "permlevel": 0,
        "read": 1,
        "print": 1,
        "report": 1,
        "share": 1,
        "parentfield": "permissions",
        "parenttype": "DocType",
        "doctype": "Custom DocPerm",
    },
]

CUSTOM_PERMS = COMPANY_PERMS + WORKFLOW_STATE_PERMS + BANK_ACCOUNT_PERMS


# Sample
# {
#     "role": "DCC Preacher",
#     "parent": "Company",
#     "permlevel": 0,
#     "read": 1,
#     "create": 1,
#     "write": 1,
#     "submit": 0,
#     "delete": 1,
#     "email": 1,
#     "export": 1,
#     "import": 1,
#     "print": 1,
#     "report": 1,
#     "set_user_permissions": 1,
#     "share": 1,
#     "parentfield": "permissions",
#     "parenttype": "DocType",
#     "doctype": "Custom DocPerm",
# }


def execute():
    records = []
    for perm in CUSTOM_PERMS:
        if not perm_exists(perm):
            records.append(perm)

    make_records(records)


def perm_exists(perm):
    filters = {"role": perm["role"], "permlevel": perm["permlevel"], "parent": perm["parent"]}
    return frappe.db.exists("Custom DocPerm", filters)
