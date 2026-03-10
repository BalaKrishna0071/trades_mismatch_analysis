
from datetime import datetime, date, timedelta
from nse_holiday_list import nse_holidays_list_2026




#  ---- Holiday Check Func  ----
def holiday_check(expiry_date: date):
    """Checks Expiry Date & Skips Holidays"""

    if isinstance(expiry_date, str):
        return datetime.strptime(expiry_date, "%Y-%m-%d").date()

    if expiry_date in nse_holidays_list_2026:
        return expiry_date - timedelta(days=1)

    return expiry_date