from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
    make_dimension_in_accounting_doctypes,
)
import frappe
from frappe.desk.page.setup_wizard.setup_wizard import make_records
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from dhananjaya.constants import INDIAN_STATES


def after_install():
    create_accounting_dimension_fields()


def create_accounting_dimension_fields():
    doctypes = frappe.get_hooks(
        "accounting_dimension_doctypes",
        app_name="dhananjaya",
    )

    dimensions = frappe.get_all("Accounting Dimension", pluck="name")
    for dimension in dimensions:
        doc = frappe.get_doc("Accounting Dimension", dimension)
        make_dimension_in_accounting_doctypes(doc, doctypes)


## The below creation of custom codes is no longer needed since we can now receive all such customisations using Fixtures. I have made a common fixtures file in hkm app. Use that and all existing things of main hkmjerp.in site will be ported to other sites as well.


# def make_custom_records():
#     records = [
#         {"doctype": "Role", "role_name": "DCC Preacher"},
#         {"doctype": "Role", "role_name": "DCC Executive"},
#         {"doctype": "Role", "role_name": "DCC Manager"},
#         {"doctype": "Role", "role_name": "DCC Cashier"},
#     ]
#     records.extend(get_states_and_actions())
#     if not frappe.db.exists("Workflow", "Donation Receipt Workflow"):
#         records.append(get_workflow())
#     make_records(records)


# def setup_dhananjaya():
#     make_custom_records()
#     make_custom_fields()
#     frappe.db.commit()
#     frappe.clear_cache()


# def make_custom_fields(update=True):
#     custom_fields = get_custom_fields()
#     create_custom_fields(custom_fields, update=update)


# def get_custom_fields():
#     custom_fields = {
#         "Journal Entry": [
#             dict(
#                 fieldname="donation_receipt",
#                 label="Donation Receipt",
#                 fieldtype="Link",
#                 options="Donation Receipt",
#                 insert_after="tax_withholding_category",
#             ),
#             dict(
#                 fieldname="bank_statement_name",
#                 label="Bank Statement Name",
#                 fieldtype="Data",
#                 insert_after="donation_receipt",
#                 hidden=1,
#                 read_only=1,
#             ),
#             dict(
#                 fieldname="workflow_state",
#                 label="Workflow State",
#                 fieldtype="Link",
#                 options="Workflow State",
#                 hidden=1,
#                 read_only=1,
#                 allow_on_submit=1,
#                 in_standard_filter=1,
#             ),
#         ],
#         "User": [
#             dict(
#                 fieldname="dhananjaya_section",
#                 label="Dhananjaya Settings",
#                 fieldtype="Section Break",
#                 insert_after="roles",
#                 collapsible=1,
#             ),
#             dict(
#                 fieldname="default_indian_state",
#                 label="Default State",
#                 fieldtype="Select",
#                 options="\n" + "\n".join(INDIAN_STATES),
#                 default="Rajasthan",
#                 insert_after="dhananjaya_section",
#             ),
#             dict(
#                 fieldname="print_reference_id",
#                 label="Print Reference ID",
#                 fieldtype="Check",
#                 insert_after="default_indian_state",
#             ),
#         ],
#     }
#     return custom_fields


# def get_states_and_actions():
#     return [
#         ## States ##
#         {
#             "doctype": "Workflow State",
#             "workflow_state_name": "Draft",
#             "style": "Primary",
#         },
#         {
#             "doctype": "Workflow State",
#             "workflow_state_name": "Acknowledged",
#             "style": "Primary",
#         },
#         {
#             "doctype": "Workflow State",
#             "workflow_state_name": "Cheque Collected",
#             "style": "Info",
#         },
#         {
#             "doctype": "Workflow State",
#             "workflow_state_name": "Suspense",
#             "style": "Warning",
#         },
#         {
#             "doctype": "Workflow State",
#             "workflow_state_name": "Received by Cashier",
#             "style": "Success",
#         },
#         {
#             "doctype": "Workflow State",
#             "workflow_state_name": "Realized",
#             "style": "Success",
#         },
#         {
#             "doctype": "Workflow State",
#             "workflow_state_name": "Cancelled",
#             "style": "Danger",
#         },
#         ## Actions ##
#         {"doctype": "Workflow Action Master", "workflow_action_name": "Acknowledge"},
#         {"doctype": "Workflow Action Master", "workflow_action_name": "Receive Cash"},
#         {"doctype": "Workflow Action Master", "workflow_action_name": "Collect Cheque"},
#         {"doctype": "Workflow Action Master", "workflow_action_name": "Confirm"},
#         {"doctype": "Workflow Action Master", "workflow_action_name": "Cancel"},
#         {"doctype": "Workflow Action Master", "workflow_action_name": "Trash"},
#     ]


# def get_workflow():
#     return {
#         "workflow_name": "Donation Receipt Workflow",
#         "document_type": "Donation Receipt",
#         "is_active": 1,
#         "override_status": 0,
#         "send_email_alert": 0,
#         "workflow_state_field": "workflow_state",
#         "doctype": "Workflow",
#         "transitions": [
#             {
#                 "idx": 1,
#                 "state": "Draft",
#                 "action": "Acknowledge",
#                 "next_state": "Acknowledged",
#                 "allowed": "DCC Preacher",
#                 "allow_self_approval": 1,
#                 "condition": "doc.donor",
#                 "parent": "Donation Receipt Workflow",
#                 "parentfield": "transitions",
#                 "parenttype": "Workflow",
#                 "doctype": "Workflow Transition",
#             },
#             {
#                 "idx": 2,
#                 "state": "Acknowledged",
#                 "action": "Receive Cash",
#                 "next_state": "Received by Cashier",
#                 "allowed": "DCC Cashier",
#                 "allow_self_approval": 1,
#                 "condition": "doc.payment_method == 'Cash'",
#                 "parent": "Donation Receipt Workflow",
#                 "parentfield": "transitions",
#                 "parenttype": "Workflow",
#                 "doctype": "Workflow Transition",
#             },
#             {
#                 "idx": 3,
#                 "state": "Acknowledged",
#                 "action": "Collect Cheque",
#                 "next_state": "Cheque Collected",
#                 "allowed": "DCC Cashier",
#                 "allow_self_approval": 1,
#                 "condition": "doc.payment_method == 'Cheque'",
#                 "parent": "Donation Receipt Workflow",
#                 "parentfield": "transitions",
#                 "parenttype": "Workflow",
#                 "doctype": "Workflow Transition",
#             },
#             {
#                 "idx": 4,
#                 "state": "Cheque Collected",
#                 "action": "Confirm",
#                 "next_state": "Realized",
#                 "allowed": "DCC Executive",
#                 "allow_self_approval": 1,
#                 "condition": "doc.payment_method == 'Cheque'",
#                 "parent": "Donation Receipt Workflow",
#                 "parentfield": "transitions",
#                 "parenttype": "Workflow",
#                 "doctype": "Workflow Transition",
#             },
#             {
#                 "idx": 5,
#                 "state": "Acknowledged",
#                 "action": "Confirm",
#                 "next_state": "Realized",
#                 "allowed": "DCC Executive",
#                 "allow_self_approval": 1,
#                 "condition": "doc.payment_method != 'Cheque'",
#                 "parent": "Donation Receipt Workflow",
#                 "parentfield": "transitions",
#                 "parenttype": "Workflow",
#                 "doctype": "Workflow Transition",
#             },
#             {
#                 "idx": 6,
#                 "state": "Draft",
#                 "action": "Confirm",
#                 "next_state": "Suspense",
#                 "allowed": "DCC Executive",
#                 "allow_self_approval": 1,
#                 "condition": "not doc.donor and (doc.payment_method != 'Cash' and doc.payment_method != 'Cheque')",
#                 "parent": "Donation Receipt Workflow",
#                 "parentfield": "transitions",
#                 "parenttype": "Workflow",
#                 "doctype": "Workflow Transition",
#             },
#         ],
#         "states": [
#             {
#                 "idx": 1,
#                 "state": "Draft",
#                 "doc_status": "0",
#                 "is_optional_state": 0,
#                 "allow_edit": "DCC Preacher",
#                 "parent": "Donation Receipt Workflow",
#                 "parentfield": "states",
#                 "parenttype": "Workflow",
#                 "doctype": "Workflow Document State",
#             },
#             {
#                 "idx": 2,
#                 "state": "Acknowledged",
#                 "doc_status": "0",
#                 "is_optional_state": 0,
#                 "allow_edit": "DCC Executive",
#                 "parent": "Donation Receipt Workflow",
#                 "parentfield": "states",
#                 "parenttype": "Workflow",
#                 "doctype": "Workflow Document State",
#             },
#             {
#                 "idx": 3,
#                 "state": "Cheque Collected",
#                 "doc_status": "0",
#                 "is_optional_state": 0,
#                 "allow_edit": "DCC Executive",
#                 "parent": "Donation Receipt Workflow",
#                 "parentfield": "states",
#                 "parenttype": "Workflow",
#                 "doctype": "Workflow Document State",
#             },
#             {
#                 "idx": 4,
#                 "state": "Received by Cashier",
#                 "doc_status": "1",
#                 "is_optional_state": 0,
#                 "allow_edit": "DCC Manager",
#                 "parent": "Donation Receipt Workflow",
#                 "parentfield": "states",
#                 "parenttype": "Workflow",
#                 "doctype": "Workflow Document State",
#             },
#             {
#                 "idx": 5,
#                 "state": "Realized",
#                 "doc_status": "1",
#                 "is_optional_state": 0,
#                 "allow_edit": "DCC Manager",
#                 "parent": "Donation Receipt Workflow",
#                 "parentfield": "states",
#                 "parenttype": "Workflow",
#                 "doctype": "Workflow Document State",
#             },
#             {
#                 "idx": 6,
#                 "state": "Suspense",
#                 "doc_status": "1",
#                 "is_optional_state": 0,
#                 "allow_edit": "DCC Manager",
#                 "parent": "Donation Receipt Workflow",
#                 "parentfield": "states",
#                 "parenttype": "Workflow",
#                 "doctype": "Workflow Document State",
#             },
#             {
#                 "idx": 7,
#                 "state": "Cancelled",
#                 "doc_status": "2",
#                 "is_optional_state": 0,
#                 "allow_edit": "DCC Manager",
#                 "parent": "Donation Receipt Workflow",
#                 "parentfield": "states",
#                 "parenttype": "Workflow",
#                 "doctype": "Workflow Document State",
#             },
#         ],
#     }
