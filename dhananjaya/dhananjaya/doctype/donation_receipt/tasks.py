from enum import Enum
from dhananjaya.dhananjaya.utils import get_credit_values
import frappe
from datetime import datetime, timedelta

from frappe.utils.data import getdate


def update_donation_calculation():
    ## Donor Data Update
    for d in frappe.db.sql(
        """
                    select donor, count(name) as times, sum(amount) as donation, max(receipt_date) as last_donation
                    from  `tabDonation Receipt` tdr
                    where (tdr.docstatus = 1) AND (tdr.donor IS NOT NULL)
                    group by tdr.donor
                    """,
        as_dict=1,
    ):
        frappe.db.set_value(
            "Donor",
            d["donor"],
            {
                "last_donation": d["last_donation"],
                "times_donated": d["times"],
                "total_donated": d["donation"],
            },
            update_modified=False,
        )
    frappe.db.commit()


def update_patron_calculation():
    class DonationType(Enum):
        PLAIN = 1
        CREDIT = 2

    patrons_map = {}
    ## Patron Data Update
    for d in frappe.db.sql(
        """
                    SELECT tp.name as patron, count(tdr.name) as times, sum(tdr.amount) as donation, 
                    MAX(CASE
                        WHEN tdr.realization_date IS NULL THEN tdr.receipt_date
                        ELSE tdr.realization_date
                    END) as last_donation
                    FROM `tabPatron` tp
                    LEFT JOIN `tabDonation Receipt` tdr
                        ON tp.name = tdr.patron AND tdr.docstatus = 1
                    GROUP BY tp.name
                    """,
        as_dict=1,
    ):
        patrons_map.setdefault(
            d["patron"],
            frappe._dict(
                last_donation=d.last_donation,
                times_donated=d.times,
                total_donated=0 if not d.donation else d.donation,
                latest_donation_type=DonationType.PLAIN,
            ),
        )
    credits_map = get_credit_values()

    for cr in frappe.db.sql(
        """
        SELECT patron,company,
            max(posting_date) as last_date, 
            sum(credits) as credits, 
            count(name) as times
        FROM `tabDonation Credit`
        WHERE patron IS NOT NULL
        GROUP BY patron, company
        """,
        as_dict=1,
    ):
        if cr["credits"]:
            amount = credits_map[cr.company] * cr.credits
            if cr.patron not in patrons_map:
                patrons_map.setdefault(
                    cr.patron,
                    frappe._dict(last_donation=None, times_donated=0, total_donated=0),
                )

            patrons_map[cr.patron].total_donated += amount
            patrons_map[cr.patron].times_donated += cr.times

            if (not patrons_map[cr.patron].last_donation) or (
                getdate(cr.last_date) > getdate(patrons_map[cr.patron].last_donation)
            ):
                patrons_map[cr.patron].last_donation = cr.last_date
                patrons_map[cr.patron].latest_donation_type = DonationType.CREDIT

    for k, v in patrons_map.items():
        latest_donation = 0
        if v.last_donation:
            if v.latest_donation_type == DonationType.PLAIN:
                latest_donation_entry = frappe.db.sql(
                    f""" 
                        SELECT patron, SUM(amount) as donation
                        FROM `tabDonation Receipt`
                        WHERE (
                        ((realization_date IS NULL) AND receipt_date = '{v.last_donation}') 
                        OR realization_date = '{v.last_donation}'
                        ) AND patron IS NOT NULL
                        AND docstatus = 1
                        AND patron = '{k}'
                        GROUP BY patron
                    """
                )
                latest_donation = latest_donation_entry[0][1]
            else:
                for cr in frappe.db.sql(
                    f""" 
                        SELECT patron,company,SUM(credits) as credits
                        FROM `tabDonation Credit`
                        WHERE posting_date = '{v.last_donation}'
                        AND patron = '{k}'
                        GROUP BY patron, company
                        """,
                    as_dict=1,
                ):
                    latest_donation += credits_map[cr.company] * cr.credits

        frappe.db.set_value(
            "Patron",
            k,
            {
                "last_donation": v["last_donation"],
                "times_donated": v["times_donated"],
                "total_donated": (
                    0 if v["total_donated"] is None else v["total_donated"]
                ),
                "latest_donation": latest_donation,
            },
            update_modified=False,
        )

    frappe.db.commit()


def update_last_donation():
    ## Patron Caluclation is together calculated above as that is short data
    donor_map = frappe.db.sql(
        """
                    select d.name as donor, 
                    case
                        WHEN realization_date IS NULL THEN max(receipt_date)
                        ELSE max(realization_date)
                    end as last_donation
                    from `tabDonor` d
                    join `tabDonation Receipt` dr
                    on dr.donor = d.name
                    where dr.docstatus = 1
                    group by d.name
                    """,
        as_dict=1,
    )
    for map in donor_map:
        frappe.db.sql(
            f"""
                        update `tabDonor` donor
                        set donor.last_donation = '{map['last_donation']}'
                        where donor.name = '{map['donor']}'
                        """
        )


def clean_dhananjaya_data():
    ## Donor Names Cleaning
    frappe.db.sql(
        """
                    UPDATE `tabDonor`
                    SET 
                        first_name = TRIM(BOTH ' ' FROM REGEXP_REPLACE(first_name, ' {2,}', ' ')),
                        last_name = TRIM(BOTH ' ' FROM REGEXP_REPLACE(last_name, ' {2,}', ' ')),
                        full_name = TRIM(BOTH ' ' FROM REGEXP_REPLACE(full_name, ' {2,}', ' '))
                    WHERE 1
                    """
    )
    frappe.db.commit()
    # Patron Names Cleaning
    frappe.db.sql(
        """
                    UPDATE `tabPatron`
                    SET
                        first_name = TRIM(BOTH ' ' FROM REGEXP_REPLACE(first_name, ' {2,}', ' ')),
                        last_name = TRIM(BOTH ' ' FROM REGEXP_REPLACE(last_name, ' {2,}', ' ')),
                        full_name = TRIM(BOTH ' ' FROM REGEXP_REPLACE(full_name, ' {2,}', ' '))
                    WHERE 1
                    """
    )


def update_realization_date():
    receipts = frappe.db.sql(
        """
                    select je.posting_date as real_date,dr.name as receipt_id
                    from `tabDonation Receipt` dr
                    join `tabJournal Entry` je
                    on je.donation_receipt = dr.name
                    where dr.realization_date IS NULL
                    """,
        as_dict=1,
    )
    for r in receipts:
        frappe.db.set_value(
            "Donation Receipt",
            r["receipt_id"],
            "realization_date",
            r["real_date"],
            update_modified=False,
        )
