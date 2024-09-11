from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from dhananjaya.constants import INDIAN_STATES

fields = {
    "User": [
        dict(
            fieldname="dhananjaya_section",
            label="Dhananjaya Settings",
            fieldtype="Section Break",
            insert_after="roles",
            collapsible=1,
        ),
        dict(
            fieldname="default_indian_state",
            label="Default State",
            fieldtype="Select",
            options="\n" + "\n".join(INDIAN_STATES),
            default="Rajasthan",
            insert_after="dhananjaya_section",
        ),
        dict(
            fieldname="print_reference_id",
            label="Print Reference ID",
            fieldtype="Check",
            insert_after="default_indian_state",
        ),
        dict(
            fieldname="default_company",
            label="Default Company",
            fieldtype="Link",
            options="Company",
            insert_after="print_reference_id",
        ),
    ],
}


def execute():
    create_custom_fields(fields, update=True)
