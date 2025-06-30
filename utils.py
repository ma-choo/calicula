# utils.py

from datetime import datetime

# Internal cache for current time
_current_time = None

month_name = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

mon_name = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
]

day_name = [
    "Sunday", "Monday", "Tuesday",
    "Wednesday", "Thursday", "Friday", "Saturday"
]

days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def init_current_time():
    """Initialize the current date (can be used once at startup)."""
    global _current_time
    _current_time = datetime.now()

def get_current_day():
    """Get the current day (1–31)."""
    return _current_time.day if _current_time else datetime.now().day

def get_current_month():
    """Get the current month (0–11, zero-based to match C logic)."""
    return (_current_time.month - 1) if _current_time else datetime.now().month - 1

def get_current_year():
    """Get the current year."""
    return _current_time.year if _current_time else datetime.now().year


def get_month_name(i: int) -> str:
    return month_name[i] if 0 <= i < 12 else "ERR"

def get_mon_name(i: int) -> str:
    return mon_name[i] if 0 <= i < 12 else "ERR"

def get_day_name(i: int) -> str:
    return day_name[i] if 0 <= i < 7 else "ERR"

def get_days_in_month(month: int) -> int:
    if 0 <= month < 12:
        return days_in_month[month]
    return 0

def determine_leap_year(year: int):
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        days_in_month[1] = 29
    else:
        days_in_month[1] = 28

def zeller(month: int, year: int) -> int:
    # Normalize month to 1-based for Zeller's Congruence
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

