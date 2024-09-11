import frappe
from datetime import datetime
from dhananjaya.dhananjaya.utils import  get_preacher_users

## SEND NOTIFICATION TO DHANANJAYA APP USERS ON VARIOUS STATES OF RECEIPTS
def notify_mobile_app_users(doc):
    settings_doc = frappe.get_cached_doc("Dhananjaya Settings")
    message = title = None
    current_time = datetime.now().strftime("%d %B, %Y %I:%M %p")
    notification_channel = None
    if doc.workflow_state == "Received by Cashier" and doc.payment_method == "Cash":
        title = f"{doc.payment_method} Acknowledgement"
        message = f"This is to acknowledge that Cashier has received a cash of Rs. {doc.amount} from you at {current_time}."
        notification_channel = settings_doc.cash_cheque_collection_channel

    elif doc.workflow_state == "Cheque Collected" and doc.payment_method == "Cheque":
        title = f"{doc.payment_method} Acknowledgement"
        message = f"This is to acknowledge that Cashier has collected a cheque of Rs. {doc.amount} from you at {current_time}."
        notification_channel = settings_doc.cash_cheque_collection_channel

    elif doc.workflow_state == "Realized" and not doc.is_ecs:
        title = f"{doc.full_name} Receipt Realised!"
        message = f"This is to inform you that donation by {doc.full_name} has been realized of Rs. {doc.amount} from Bank Statement."
        notification_channel = settings_doc.receipt_realisation_channel

    elif doc.workflow_state == "Realized" and doc.is_ecs:
        title = f"{doc.full_name} ECS Ready!"
        message = f"This is to inform you that ECS donation by {doc.full_name} has been realized of Rs. {doc.amount} from Bank Statement."
        notification_channel = settings_doc.ecs_channel

    # IF Message is Ready!
    if title is not None:
        erp_users = []
        if not doc.preacher:
            erp_users = [doc.owner]
        else:
            # erp_user = frappe.db.get_value(
            #     "LLP Preacher", doc.preacher, "erp_user"
            # )
            erp_users = get_preacher_users(doc.preacher)
        for erp_user in erp_users:
            notif_doc = frappe.get_doc(
                {
                    "doctype": "App Notification",
                    "app": settings_doc.firebase_admin_app,
                    "channel": notification_channel,
                    "user": erp_user,
                    "subject": title,
                    "message": message,
                    "is_route": 1,
                    "route": f"/donation_receipt/{doc.name}",
                }
            )
            notif_doc.insert(ignore_permissions=True)
