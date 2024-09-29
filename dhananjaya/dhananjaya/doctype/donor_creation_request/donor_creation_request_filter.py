import frappe
from dhananjaya.constants import DCC_EXCLUDE_ROLES
from dhananjaya.dhananjaya.utils import get_preachers


def list(user):
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    full_access = any(role in DCC_EXCLUDE_ROLES for role in user_roles)

    if full_access:
        return "( 1 )"

    # return "( 1 )"

    preachers = get_preachers()

    if len(preachers) == 0:
        return "( 0 )"
    else:
        preachers_str = ",".join([f"'{p}'" for p in preachers])
        return f" ( `llp_preacher` in ( {preachers_str} ) ) "


def single(doc, user=None, permission_type=None):
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    full_access = any(role in DCC_EXCLUDE_ROLES for role in user_roles)

    if full_access or (doc.llp_preacher in get_preachers()):
        return True

    return False
