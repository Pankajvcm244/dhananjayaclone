import re, json
import frappe


@frappe.whitelist()
def upload_donation_from_temp_donor_upload():
    temp_donors = frappe.get_all("Temp Donor Upload", fields=["*"])
    for t in temp_donors:
        upload_donation(t)


@frappe.whitelist()
def upload_donation(t):
    # temp_donors = frappe.get_all("Temp Donor Upload", fields=["*"])
    # # pan_nos = [
    # for t in temp_donors:
    if isinstance(t, str):
        t = json.loads(t)
    if (t["preacher"] is None) or (t["preacher"] == ""):
        preacher = "DCC"
    else:
        t["preacher"] = t["preacher"].rstrip()
        preachers = frappe.get_all(
            "LLP Preacher", filters={"name": t["preacher"]}, fields=["name"]
        )
        if len(preachers) > 0:
            preacher = preachers[0]["name"]
        else:
            doc = frappe.get_doc(
                {
                    "doctype": "LLP Preacher",
                    "full_name": t["preacher"],
                    "initial": t["preacher"],
                }
            )
            doc.insert(ignore_permissions=True)
            preacher = doc.name

    donor = None

    clean_pan = None
    if t["pan_no"]:
        clean_pan = re.sub(r"\s+", "", t["pan_no"])
        pan_donors = frappe.db.sql(
            f"""
                select name
                from `tabDonor`
                where REGEXP_REPLACE(pan_no, '\\s+', '') = '{clean_pan}'
                """,
            as_dict=1,
        )
        if len(pan_donors) > 0:
            donor = pan_donors[0]["name"]

    clean_contact = None
    if (donor is None) and t["mobile"]:
        clean_contact = re.sub(r"\D", "", t["mobile"])[-10:]
        contacts = frappe.db.sql(
            f"""
                select contact_no,parent
                from `tabDonor Contact`
                where REGEXP_REPLACE(contact_no, '[^0-9]+', '') LIKE '%{clean_contact}%' and parenttype = 'Donor'
                """,
            as_dict=1,
        )
        if len(contacts) > 0:
            donor = contacts[0]["parent"]

    if donor is None:
        donor_dict = {
            "doctype": "Donor",
            "first_name": t["donor_name"],
            "llp_preacher": preacher,
        }

        if t["address"]:
            resolved_address = parseFullAddress(t["address"])

            address_single = [
                {
                    "address_line_1": resolved_address[0],
                    "city": resolved_address[1],
                    "state": resolved_address[2],
                    "pin_code": resolved_address[4],
                }
            ]

            donor_dict.update({"addresses": address_single})
        
        if ("email" in t) and t["email"]:
            donor_dict.update({"emails": [{
                'email':t['email']
            }]})

        if clean_contact is not None:
            donor_dict.update({"contacts": [{"contact_no": clean_contact}]})

        if clean_pan is not None:
            donor_dict.update({"pan_no": clean_pan})

        donor_doc = frappe.get_doc(donor_dict)

        donor_doc.insert()

        donor = donor_doc.name

    ### Upload Receipts
    llp_preacher = frappe.db.get_value("Donor", donor, "llp_preacher")
    receipt_dict = {
            "doctype": "Donation Receipt",
            "company": "Hare Krishna Movement Mumbai",
            "receipt_date": t["date"],
            "preacher": llp_preacher,
            "donor": donor,
            "contact": t["mobile"],
            "address": t["address"],
            "payment_method": t["mode_of_payment"],
            "amount": t["amount"],
            "remarks": t["remarks"],
            "seva_type": "General Donation - HKMM",
            "old_dr_no": t["dr_no"],
        }

    if "additional_charges" in t:
        receipt_dict["additional_charges"] = t["additional_charges"]
    
    receipt_doc = frappe.get_doc(receipt_dict)
    receipt_doc.insert(ignore_permissions=True)

    if "status" in t and t["status"] == "Acknowledged":
        receipt_doc.db_set("workflow_state", t['status'])
        receipt_doc.db_set("docstatus", 0)
    elif "status" not in t or t["status"] in ["Realized","Received by Cashier"]:
        if t["mode_of_payment"]  == "Cash":
            receipt_doc.db_set("workflow_state", "Received by Cashier")
        else:
            receipt_doc.db_set("workflow_state", "Realized")
        receipt_doc.db_set("docstatus", 1)
    else:
        frappe.throw('Status can only be one of ["Acknowledged", "Realized","Received by Cashier"]')

    frappe.db.commit()

    return {
        "receipt_id":receipt_doc.name,
        "donor_id": donor
    }


STATES = "|".join(
    [
        "Andhra Pradesh",
        "Arunachal Pradesh",
        "Assam",
        "Bihar",
        "Chhattisgarh",
        "Goa",
        "Gujarat",
        "Haryana",
        "Himachal Pradesh",
        "Jharkhand",
        "Karnataka",
        "Kerala",
        "Madhya Pradesh",
        "Maharashtra",
        "Manipur",
        "Meghalaya",
        "Mizoram",
        "Nagaland",
        "Odisha",
        "Punjab",
        "Rajasthan",
        "Sikkim",
        "Tamil Nadu",
        "Telangana",
        "Tripura",
        "Uttar Pradesh",
        "Uttarakhand",
        "West Bengal",
    ]
)

CITIES = "|".join(
    [
        "Mumbai",
        "Delhi",
        "Bangalore",
        "Hyderabad",
        "Ahmedabad",
        "Chennai",
        "Kolkata",
        "Surat",
        "Pune",
        "Jaipur",
        "Lucknow",
        "Kanpur",
        "Nagpur",
        "Indore",
        "Thane",
        "Bhopal",
        "Visakhapatnam",
        "Pimpri & Chinchwad",
        "Patna",
        "Vadodara",
        "Ghaziabad",
        "Ludhiana",
        "Agra",
        "Nashik",
        "Faridabad",
        "Meerut",
        "Rajkot",
        "Kalyan & Dombivali",
        "Vasai Virar",
        "Varanasi",
        "Srinagar",
        "Aurangabad",
        "Dhanbad",
        "Amritsar",
        "Navi Mumbai",
        "Prayagraj",
        "Ranchi",
        "Haora",
        "Coimbatore",
        "Jabalpur",
        "Gwalior",
        "Vijayawada",
        "Jodhpur",
        "Madurai",
        "Raipur",
        "Kota",
        "Guwahati",
        "Chandigarh",
        "Solapur",
        "Hubli and Dharwad",
        "Bareilly",
        "Moradabad",
        "Karnataka",
        "Gurgaon",
        "Aligarh",
        "Jalandhar",
        "Tiruchirappalli",
        "Bhubaneswar",
        "Salem",
        "Mira and Bhayander",
        "Thiruvananthapuram",
        "Bhiwandi",
        "Saharanpur",
        "Gorakhpur",
        "Guntur",
        "Bikaner",
        "Amravati",
        "Noida",
        "Jamshedpur",
        "Bhilai Nagar",
        "Warangal",
        "Cuttack",
        "Firozabad",
        "Kochi",
        "Bhavnagar",
        "Dehradun",
        "Durgapur",
        "Asansol",
        "Nanded Waghala",
        "Kolapur",
        "Ajmer",
        "Gulbarga",
        "Jamnagar",
        "Ujjain",
        "Loni",
        "Siliguri",
        "Jhansi",
        "Ulhasnagar",
        "Nellore",
        "Jammu",
        "Sangli Miraj Kupwad",
        "Belgaum",
        "Mangalore",
        "Ambattur",
        "Tirunelveli",
        "Malegoan",
        "Gaya",
        "Jalgaon",
        "Udaipur",
        "Maheshtala",
    ]
)


def parseFullAddress(address):
    extract_pin = re.search(r"\b\d{6}\b", address)
    if not extract_pin:
        pin_code = ""
    else:
        address = re.sub(r"\b\d{6}\b", "", address)
        pin_code = extract_pin.group(0)

    extract_state = re.search(STATES, address, re.IGNORECASE)
    if not extract_state:
        state = ""
    else:
        address = re.sub(STATES, "", address, flags=re.IGNORECASE)
        state = extract_state.group(0)

    extract_city = re.search(CITIES, address, re.IGNORECASE)
    if not extract_city:
        city = ""
    else:
        address = re.sub(CITIES, "", address, flags=re.IGNORECASE)
        city = extract_city.group(0)

    extract_country = re.search("INDIA", address, re.IGNORECASE)
    if not extract_country:
        country = ""
    else:
        address = re.sub("INDIA", "", address, flags=re.IGNORECASE)
        country = extract_country.group(0)

    try:
        address = address.rstrip()
        while address[-1] in [" ", ",", "-", "_", "."]:
            address = address[:-1]
        while address[1] in [" ", ",", "-", "_", "."]:
            address = address[1:]
    except:
        print("-")

    if not address:
        address = "-"

    return [address, city, state.title(), country, pin_code]
