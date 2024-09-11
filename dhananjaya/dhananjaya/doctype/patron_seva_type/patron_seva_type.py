# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class PatronSevaType(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        enabled: DF.Check
        included_in_commitment_status: DF.Check
        privilege_pujas: DF.Int
        seva_amount: DF.Currency
        seva_code: DF.Data | None
        seva_name: DF.Data | None
    # end: auto-generated types
    pass
