import frappe
from dhananjaya.constants import DCC_EXCLUDE_ROLES
from dhananjaya.dhananjaya.utils import get_preachers
yatra_manager = "Yatra Manager"

def list(user):
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    full_access = any(role in DCC_EXCLUDE_ROLES for role in user_roles)

    if full_access or yatra_manager in user_roles:
        return "( 1 )"

    # return "( 1 )"

    preachers = get_preachers()

    if len(preachers) == 0:
        return "( 0 )"
    else:
        preachers_str = ",".join([f"'{p}'" for p in preachers])
        return f" ( `preacher` in ( {preachers_str} ) ) "

def single(doc, user=None, permission_type=None):
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    full_access = any(role in DCC_EXCLUDE_ROLES for role in user_roles)
    donor_preacher = frappe.db.get_value("Donor" , doc.donor, "llp_preacher");

    donor_request_preacher = frappe.db.get_value("Donor Creation Request", doc.donor_creation_request, "llp_preacher"); 
    
    if full_access or (donor_preacher in get_preachers())  or (donor_request_preacher in get_preachers()) or yatra_manager in user_roles:
        print("full_access or (doc.preacher in get_preachers())");
        return True

        

    return False
