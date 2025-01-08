from datetime import datetime, timedelta
from warnings import filters

from attr import field
import frappe
from frappe.model import workflow
def auto_cancel_yatra_registration():
   
    for i in  frappe.get_all(
        "Seva Subtype",
        filters={
            "is_a_yatra": 1, 
            "enabled": 1,
            # "from_date": ["<", datetime.now().strftime("%Y-%m-%d")]
            },
        fields=["name" , "auto_cancel"]
    ):
        if not i.auto_cancel or i.auto_cancel == 0:
            continue
        
        past_date_str = (
        datetime.now() - timedelta(days=i.auto_cancel)
                ).strftime("%Y-%m-%d")
        
        
        for j in frappe.get_all(
            "Yatra Registration",
            filters={
                "seva_subtype": i.name,
                "creation": ["<", past_date_str],
                "docstatus": 1,
            },
            
            fields=["name" , "donor_name"],
        ):  
            if not frappe.db.exists(
                "Donation Receipt",
                {
                    "seva_subtype": i.name,
                    "yatra_registration": j.name,
                    "docstatus": ["!=", 2],
                    "workflow_state" : ['!=', 'Trashed'],
                },
            ):
                frappe.get_doc("Yatra Registration", j.name).cancel()
        
    frappe.db.commit()
    return