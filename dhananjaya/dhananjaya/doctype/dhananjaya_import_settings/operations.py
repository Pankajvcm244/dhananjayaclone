import frappe, itertools
from rapidfuzz import process, fuzz
from frappe.utils.csvutils import build_csv_response




@frappe.whitelist()
def get_data_for_analysis(*args,**kwargs):
    data = [['address','erp_id','old_id','full_name']]
    rows = frappe.db.sql("""
                    select REPLACE(concat(COALESCE(cta.address_line_1,"")," ",COALESCE(cta.address_line_2,"")), ',', ' ' )  as address,
                        dr.name as erp_id,
                        dr.old_donor_id as old_id,
                        dr.full_name
                    from `tabDonor` dr
                    join `tabDonor Address` cta
                    on cta.parent = dr.name
                    where 1
                    """,as_dict=0)
    
    build_csv_response(data+list(rows),"donor")

@frappe.whitelist()
def get_template_for_merging_donors(*args,**kwargs):
    data = [['erp_id_merge_to','erp_id_to_be_merged']]
    build_csv_response(data,"template_for_merging_donors")

@frappe.whitelist()
def merge_donors(*args,**kwargs):
    from frappe.utils.csvutils import read_csv_content
    settings = frappe.get_cached_doc("Dhananjaya Import Settings")
    _file = frappe.get_doc("File", {"file_url": settings.upload_merge_file})
    fcontent = _file.get_content()
    rows = read_csv_content(fcontent)
    for row in rows[1:]:
        merge_to = frappe.get_doc("Donor",row[0])
        merge_from = frappe.get_doc("Donor",row[1])

        mi_addresses = {add.type:{'doc_name':add.name,'full_add':full_address(add)} for add in merge_to.addresses}
        for address in merge_from.addresses:
            # return address.type
            if (address.type in mi_addresses) and len(full_address(address))>len(mi_addresses[address.type]['full_add']):
                frappe.delete_doc("Donor Address", mi_addresses[address.type]['doc_name'])
                address.parent = merge_to.name
                address.save()
            elif address.type not in mi_addresses:
                address.parent = merge_to.name
                address.save()

        contacts = [c.contact_no  for c in merge_to.contacts ]
        for con in merge_from.contacts:
            if (not con in contacts):
                con.parent = merge_to.name
                con.save()
        emails = [c.email  for c in merge_to.emails ]
        for em in merge_from.emails:
            if (not em.email in emails):
                em.parent = merge_to.name
                em.save()
        relatives = [c.relation  for c in merge_to.family_members ]
        for mem in merge_from.family_members:
            if (not mem.relation in relatives):
                mem.parent = merge_to.name
                mem.save()
        
        merge_to.old_donor_id = (if_none(merge_to.old_donor_id)+","+if_none(merge_from.old_donor_id)).strip(',')
        merge_to.old_patron_id = (if_none(merge_to.old_patron_id)+","+if_none(merge_from.old_patron_id)).strip(',')
        merge_to.unresolved_fax_column = (if_none(merge_to.unresolved_fax_column)+","+if_none(merge_from.unresolved_fax_column)).strip(',')

        if merge_from.is_patron:
            merge_to.is_patron = 1
        if merge_from.pan_no:
            if merge_to.pan_no:
                merge_to.pan_no = merge_to.pan_no +","+merge_from.pan_no
            else:
                merge_to.pan_no = merge_from.pan_no
        if merge_from.aadhar_no:
            merge_to.aadhar_no = merge_from.aadhar_no
        if merge_from.driving_license:
            merge_to.driving_license = merge_from.driving_license
        if merge_from.passport:
            merge_to.passport = merge_from.passport
        
        merge_to.save(ignore_permissions=True)
        
        frappe.db.commit()
    #     # frappe.db.sql(f"""
	# 	# 				update `tabDonor`
	# 	# 				set is_patron=1,old_patron_id='{row[1]}'
	# 	# 				where old_donor_id = '{row[0]}'
	# 	# 				""")
	# frappe.db.commit()

def full_address(add):
    return f'{add.address_line_1} {add.address_line_2}'

def if_none(val):
    if val is None:
        return""
    return val


# def randomword(length):
#    letters = string.ascii_lowercase
#    return ''.join(random.choice(letters) for i in range(length))

# @frappe.whitelist()
# def get_similar_donors(*args,**kwargs):
#     frappe.db.delete("Dhananjaya Import Similar Address")
#     settings = frappe.get_cached_doc("Dhananjaya Import Settings")
#     test_string = f" limit {settings.test_run_records}" if settings.is_a_test else ""
    
#     addresses = frappe.db.sql(f"""
#                     select concat(COALESCE(cta.address_line_1,"")," ",COALESCE(cta.address_line_2,"")) as address,
#                         dr.name as erp_id,
#                         dr.old_donor_id as old_id,
#                         dr.full_name
#                     from `tabDonor` dr
#                     join `tabDonor Address` cta
#                     on cta.parent = dr.name
#                     where 1 {test_string}
#                     """,as_dict=1)
#     addresse_pairs = itertools.combinations(addresses, 2)
#     addresse_pairs = list(filter(lambda c: (check_basics(c[0],c[1],settings)), addresse_pairs))
#     n = 100000
#     pairs_chunk = [addresse_pairs[i * n:(i + 1) * n] for i in range((len(addresse_pairs) + n - 1) // n )]
#     for pair_chunk in pairs_chunk:
#         frappe.enqueue(get_chunk_similar, queue='short',job_name="Initial Chunk",timeout=10000,chunk_pair=pair_chunk)
#     # for i,pair in enumerate(addresse_pairs):
#     #     frappe.enqueue(match_two_address, queue='long',job_name="Comparing Donors",timeout=100000,pair=pair)

# def get_chunk_similar(chunk_pair):
#     for pair in chunk_pair:
#         frappe.enqueue(match_two_address, queue='long',job_name="Comparing Donors in Chunk",timeout=100000,pair=pair)

# def check_basics(ref,tgt,settings):
#     if ref['old_id'] == tgt['old_id']:
#         return False
#     if ref['address'].strip() == "" or tgt['address'].strip() == "":
#         return False
#     if len(ref['address']) < settings.minimum_character or len(tgt['address']) < settings.minimum_character:
#         return False
#     return True


# def match_two_address(pair):
#     settings = frappe.get_cached_doc("Dhananjaya Import Settings")
#     ref,tgt = pair
#     allow_ratio = settings.similar_ratio_allowed
#     # if not (fuzz.token_sort_ratio(ref['full_name'],tgt['full_name'])>allow_ratio):
#     #     return
#     if fuzz.token_sort_ratio(ref['address'],tgt['address'])>allow_ratio:
#         row = {   
#                 "ref_address":ref['address'],
#                 "target_address":tgt['address'],
#                 "ref_name":ref['full_name'],
#                 "target_name":tgt['full_name'],
#                 "ref_erp_id":ref['erp_id'],
#                 "target_erp_id":tgt['erp_id'],
#                 "ref_old_id":ref['old_id'],
#                 "target_old_id":tgt['old_id']
#             }
#         frappe.enqueue(insert_similar_address_data, queue='short',job_name="Inserting Similar Address Data",timeout=10000,row = row)
#         #insert_similar_address_data(row)
# def insert_similar_address_data(row):
#     row.setdefault('doctype','Dhananjaya Import Similar Address')
#     doc = frappe.get_doc(row)
#     doc.insert(ignore_if_duplicate=True)