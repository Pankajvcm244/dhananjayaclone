import datetime

from frappe.utils.data import add_to_date

def get_ecs_months(start_date, periodicity):
    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')

    months_dict = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December"
    }
    steps = {
        "Y":12,
        "H":6,
        "Q":3,
        "M":1
    }[periodicity]

    months = {}
    
    current_month = start_date.month

    for i in range(current_month, current_month+12, steps):
        key = i%12 if i%12 != 0 else 12
        months.update({key : months_dict[key]})
    
    return months

def count_of_ecs(start_date, periodicity, closing_date):
    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')

    if isinstance(closing_date, str):
        closing_date = datetime.datetime.strptime(closing_date, '%Y-%m-%d')
    
    steps = {
        "Y":12,
        "H":6,
        "Q":3,
        "M":1
    }[periodicity]

    count = 0
    beg_date = start_date
    
    while beg_date <= closing_date:
        count += 1
        beg_date = add_to_date(beg_date, months=steps)
    
    return count


