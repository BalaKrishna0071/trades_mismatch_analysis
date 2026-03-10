

from holidays_utils import holiday_check
from datetime import datetime, timedelta, date
from nse_holiday_list import nse_holidays_list_2026




# ----- Current Expiry Func ---
def current_expiry(today=None, time_=None):
    """Gives Expiry Dates"""

    if today is None and time_ is None:
        today = datetime.today().date()
        time_ = datetime.today().time().strftime("%H:%M")

    elif isinstance(today, date):
        today = today.date()
        if time_ is None:
            time_ = date.today().strftime("%H:%M")

    # print(f"| Today: {today} | Time: {time_} ! ")

    weekday = today.weekday()
    start_of_week = today - timedelta(days=weekday)
    tuesday = start_of_week + timedelta(days=1)
    thursday = start_of_week + timedelta(days=3)
    prev_thursday = start_of_week - timedelta(days=4)

    # Holiday Check
    tuesday_expiry_date = holiday_check(tuesday)
    thursday_expiry_date = holiday_check(thursday)
    previous_thursday_expiry_date = holiday_check(prev_thursday)

    current_time = datetime.strptime(time_, "%H:%M").time()
    market_end = datetime.strptime("03:40", "%H:%M").time()
    market_start = datetime.strptime("09:15", "%H:%M").time()

    # print(f"Weekday: {weekday} & Start Week: {start_of_week} & Tuesday: {tuesday_expiry_date} & Thursday: {thursday_expiry_date} & Previous Thursday: {previous_thursday_expiry_date} !")

    if weekday == 0 and current_time <= market_start:
        return previous_thursday_expiry_date
    if weekday == 0 and current_time > market_end:
        return previous_thursday_expiry_date
    elif weekday == 1 and current_time < market_start:
        return previous_thursday_expiry_date
    elif weekday == 1 and current_time > market_end:
        return tuesday_expiry_date
    elif weekday == 2 and current_time < market_start:
        return tuesday_expiry_date
    elif weekday == 2 and current_time > market_end:
        return tuesday_expiry_date
    elif weekday == 3 and current_time < market_start:
        return tuesday_expiry_date
    elif weekday == 3 and current_time > market_end:
        return thursday_expiry_date
    else:
        return thursday_expiry_date

