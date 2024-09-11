import frappe
def execute():
    entries = frappe.db.sql("""
                            select td.name as donor
                            from `tabDonor` td
                            join `tabDonor Address` tda on td.name = tda.parent 
                            where tda.address_line_1  = ""
                            group by donor
                            """,as_dict=1)
    for e in entries:
        donor = frappe.get_doc("Donor",e['donor'])
        indexes = []
        for index,a in enumerate(donor.addresses):
            if a.address_line_1 == "":
                indexes.append(index)
        for index in sorted(indexes, reverse=True):
            del donor.addresses[index]
        donor.save()
