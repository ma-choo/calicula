# utils.py - date/time utility functions
# TODO: lots of normalization going on here currently. maybe refactor to make it less confusing?

import calendar
from datetime import date, datetime

def contains_bad_chars(name: str) -> bool:
    invalid_chars = {'\t', '\n', '\r', '\x1b', ',' '<', '>', ':', '"', '/', '\\', '|'}
    if any(ch in invalid_chars for ch in name):
        return True
    if any(ord(ch) < 32 for ch in name):  # check for ascii control chars
        return True
    return False

def get_current_day():
    return datetime.now().day

def get_current_month():
    return datetime.now().month - 1  # zero-based for internal logic

def get_current_year():
    return datetime.now().year

def get_day_name(index: int) -> str:
    day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    return day_names[index]

def get_day_date_name(d: date | datetime) -> str:
    return calendar.day_name[d.weekday()]

# TODO: replace this with a function from the calendar module
def get_month_name(month_num):
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    return month_names[month_num]

def get_mon_name(month_num):
    return get_month_name(month_num)[:3]

def get_days_in_month(month, year=None):
    if year is None:
        year = datetime.now().year
    month += 1  # convert from 0-based to 1-based
    if month == 2:
        # leap year check
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            return 29
        return 28
    if month in [4, 6, 9, 11]:
        return 30
    return 31

# zeller's algorithm: used for getting a first day offset for proper calendar view display
def zeller(month, year):
    # normalize month to 1-based
    month += 1
    day = 1
    if month < 3:
        z_month = month + 10
        z_year = year - 1
    else:
        z_month = month - 2
        z_year = year

    offset = ((13 * z_month - 1) // 5 + day + z_year % 100 +
              (z_year % 100) // 4 - 2 * (z_year // 100) +
              (z_year // 400) + 77) % 7
    return offset