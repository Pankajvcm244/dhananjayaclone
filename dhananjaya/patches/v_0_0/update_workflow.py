import json
import frappe
from frappe.desk.form.save import savedocs
from frappe.desk.page.setup_wizard.setup_wizard import make_records
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    make_custom_records()

def make_custom_records():
    records = [
        {"doctype": "Role", "role_name": "DCC Preacher"},
        {"doctype": "Role", "role_name": "DCC Executive"},
        {"doctype": "Role", "role_name": "DCC Manager"},
        {"doctype": "Role", "role_name": "DCC Cashier"},
    ]
    records.extend(get_states_and_actions())

    # if not frappe.db.exists("Workflow", "Donation Receipt Workflow"):
    # 	records.append(get_workflow())
    make_records(records)

    try:
        workflow_doc = frappe.get_doc("Workflow", "Donation Receipt Workflow")
    except:
        workflow_doc = frappe.new_doc("Workflow")
    workflow_data = get_workflow()

    workflow_doc.update(workflow_data)
    workflow_doc.save()


def get_states_and_actions():
    return [
        ## States ##
        {
            "doctype": "Workflow State",
            "workflow_state_name": "Draft",
            "style": "Primary",
        },
        {
            "doctype": "Workflow State",
            "workflow_state_name": "Acknowledged",
            "style": "Primary",
        },
        {
            "doctype": "Workflow State",
            "workflow_state_name": "Cheque Collected",
            "style": "Info",
        },
        {
            "doctype": "Workflow State",
            "workflow_state_name": "Suspense",
            "style": "Warning",
        },
        {
            "doctype": "Workflow State",
            "workflow_state_name": "Received by Cashier",
            "style": "Success",
        },
        {
            "doctype": "Workflow State",
            "workflow_state_name": "Realized",
            "style": "Success",
        },
        {
            "doctype": "Workflow State",
            "workflow_state_name": "Cancelled",
            "style": "Danger",
        },
        {
            "doctype": "Workflow State",
            "workflow_state_name": "ECS Rejected",
            "style": "Danger",
        },
        {
            "doctype": "Workflow State",
            "workflow_state_name": "Trashed",
            "style": "Danger",
        },
        {
            "doctype": "Workflow State",
            "workflow_state_name": "Bounced",
            "style": "Danger",
        },
        ## Actions ##
        {"doctype": "Workflow Action Master", "workflow_action_name": "Acknowledge"},
        {"doctype": "Workflow Action Master", "workflow_action_name": "Receive Cash"},
        {"doctype": "Workflow Action Master", "workflow_action_name": "Collect Cheque"},
        {"doctype": "Workflow Action Master", "workflow_action_name": "Confirm"},
        {"doctype": "Workflow Action Master", "workflow_action_name": "Cancel"},
        {"doctype": "Workflow Action Master", "workflow_action_name": "Trash"},
        {"doctype": "Workflow Action Master", "workflow_action_name": "Bounce"},
        {"doctype": "Workflow Action Master", "workflow_action_name": "Prepare"},
    ]


def get_workflow():
    return {
        "workflow_name": "Donation Receipt Workflow",
        "document_type": "Donation Receipt",
        "is_active": 1,
        "override_status": 0,
        "send_email_alert": 0,
        "workflow_state_field": "workflow_state",
        "doctype": "Workflow",
        "transitions": [
            {
                "idx": 1,
                "state": "Draft",
                "action": "Acknowledge",
                "next_state": "Acknowledged",
                "allowed": "DCC Preacher",
                "allow_self_approval": 1,
                "condition": "doc.donor",
                "parent": "Donation Receipt Workflow",
                "parentfield": "transitions",
                "parenttype": "Workflow",
                "doctype": "Workflow Transition",
            },
            {
                "idx": 2,
                "state": "Acknowledged",
                "action": "Receive Cash",
                "next_state": "Received by Cashier",
                "allowed": "DCC Cashier",
                "allow_self_approval": 1,
                "condition": "doc.payment_method == 'Cash'  and (doc.donor or doc.donor_creation_request)",
                "parent": "Donation Receipt Workflow",
                "parentfield": "transitions",
                "parenttype": "Workflow",
                "doctype": "Workflow Transition",
            },
            {
                "idx": 3,
                "state": "Acknowledged",
                "action": "Collect Cheque",
                "next_state": "Cheque Collected",
                "allowed": "DCC Cashier",
                "allow_self_approval": 1,
                "condition": "doc.payment_method == 'Cheque'",
                "parent": "Donation Receipt Workflow",
                "parentfield": "transitions",
                "parenttype": "Workflow",
                "doctype": "Workflow Transition",
            },
            {
                "idx": 4,
                "state": "Cheque Collected",
                "action": "Confirm",
                "next_state": "Realized",
                "allowed": "DCC Executive",
                "allow_self_approval": 1,
                "condition": "doc.payment_method == 'Cheque'",
                "parent": "Donation Receipt Workflow",
                "parentfield": "transitions",
                "parenttype": "Workflow",
                "doctype": "Workflow Transition",
            },
            {
                "idx": 5,
                "state": "Acknowledged",
                "action": "Confirm",
                "next_state": "Realized",
                "allowed": "DCC Executive",
                "allow_self_approval": 1,
                "condition": "doc.payment_method not in ['Cheque','Cash']",
                "parent": "Donation Receipt Workflow",
                "parentfield": "transitions",
                "parenttype": "Workflow",
                "doctype": "Workflow Transition",
            },
            {
                "idx": 6,
                "state": "Draft",
                "action": "Confirm",
                "next_state": "Suspense",
                "allowed": "DCC Executive",
                "allow_self_approval": 1,
                "condition": "not doc.donor and (doc.payment_method != 'Cash' and doc.payment_method != 'Cheque')",
                "parent": "Donation Receipt Workflow",
                "parentfield": "transitions",
                "parenttype": "Workflow",
                "doctype": "Workflow Transition",
            },
            {
                "idx": 7,
                "state": "Acknowledged",
                "action": "Trash",
                "next_state": "Trashed",
                "allowed": "DCC Executive",
                "allow_self_approval": 1,
                "parent": "Donation Receipt Workflow",
                "parentfield": "transitions",
                "parenttype": "Workflow",
                "doctype": "Workflow Transition",
            },
            {
                "idx": 8,
                "state": "Trashed",
                "action": "Prepare",
                "next_state": "Acknowledged",
                "allowed": "DCC Executive",
                "allow_self_approval": 1,
                "parent": "Donation Receipt Workflow",
                "parentfield": "transitions",
                "parenttype": "Workflow",
                "doctype": "Workflow Transition",
            },
            {
                "idx": 9,
                "state": "Cheque Collected",
                "action": "Trash",
                "next_state": "Trashed",
                "allowed": "DCC Executive",
                "allow_self_approval": 1,
                "parent": "Donation Receipt Workflow",
                "parentfield": "transitions",
                "parenttype": "Workflow",
                "doctype": "Workflow Transition",
            },
        ],
        "states": [
            {
                "idx": 1,
                "state": "Draft",
                "doc_status": "0",
                "is_optional_state": 0,
                "allow_edit": "DCC Preacher",
                "parent": "Donation Receipt Workflow",
                "parentfield": "states",
                "parenttype": "Workflow",
                "doctype": "Workflow Document State",
            },
            {
                "idx": 2,
                "state": "Acknowledged",
                "doc_status": "0",
                "is_optional_state": 0,
                "allow_edit": "DCC Executive",
                "parent": "Donation Receipt Workflow",
                "parentfield": "states",
                "parenttype": "Workflow",
                "doctype": "Workflow Document State",
            },
            {
                "idx": 3,
                "state": "Cheque Collected",
                "doc_status": "0",
                "is_optional_state": 0,
                "allow_edit": "DCC Executive",
                "parent": "Donation Receipt Workflow",
                "parentfield": "states",
                "parenttype": "Workflow",
                "doctype": "Workflow Document State",
            },
            {
                "idx": 4,
                "state": "Received by Cashier",
                "doc_status": "1",
                "is_optional_state": 0,
                "allow_edit": "DCC Manager",
                "parent": "Donation Receipt Workflow",
                "parentfield": "states",
                "parenttype": "Workflow",
                "doctype": "Workflow Document State",
            },
            {
                "idx": 5,
                "state": "Realized",
                "doc_status": "1",
                "is_optional_state": 0,
                "allow_edit": "DCC Manager",
                "parent": "Donation Receipt Workflow",
                "parentfield": "states",
                "parenttype": "Workflow",
                "doctype": "Workflow Document State",
            },
            {
                "idx": 6,
                "state": "Suspense",
                "doc_status": "1",
                "is_optional_state": 0,
                "allow_edit": "DCC Manager",
                "parent": "Donation Receipt Workflow",
                "parentfield": "states",
                "parenttype": "Workflow",
                "doctype": "Workflow Document State",
            },
            {
                "idx": 7,
                "state": "Cancelled",
                "doc_status": "2",
                "is_optional_state": 0,
                "allow_edit": "DCC Manager",
                "parent": "Donation Receipt Workflow",
                "parentfield": "states",
                "parenttype": "Workflow",
                "doctype": "Workflow Document State",
            },
            {
                "idx": 8,
                "state": "ECS Rejected",
                "doc_status": "0",
                "is_optional_state": 0,
                "allow_edit": "System Manager",
                "parent": "Donation Receipt Workflow",
                "parentfield": "states",
                "parenttype": "Workflow",
                "doctype": "Workflow Document State",
            },
            {
                "idx": 8,
                "state": "Trashed",
                "doc_status": "0",
                "is_optional_state": 0,
                "allow_edit": "System Manager",
                "parent": "Donation Receipt Workflow",
                "parentfield": "states",
                "parenttype": "Workflow",
                "doctype": "Workflow Document State",
            },
            {
                "idx": 9,
                "state": "Bounced",
                "doc_status": "2",
                "is_optional_state": 0,
                "allow_edit": "System Manager",
                "parent": "Donation Receipt Workflow",
                "parentfield": "states",
                "parenttype": "Workflow",
                "doctype": "Workflow Document State",
            },
        ],
    }
