import re


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
