"""
DateTime conversion utilities for the service station operations bot.

Handles timezone conversions and date formatting for the Africa/Blantyre timezone.
"""

import logging
from datetime import datetime, date, timezone, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# Africa/Blantyre timezone (UTC+2)
BLANTYRE_TZ_OFFSET = 2

def get_blantyre_now() -> datetime:
    """Get current datetime in Blantyre timezone."""
    utc_now = datetime.now(timezone.utc)
    blantyre_tz = timezone(timedelta(hours=BLANTYRE_TZ_OFFSET))
    return utc_now.astimezone(blantyre_tz)

def get_blantyre_today() -> date:
    """Get current date in Blantyre timezone."""
    return get_blantyre_now().date()

def utc_to_blantyre(utc_dt: datetime) -> datetime:
    """Convert UTC datetime to Blantyre timezone."""
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    
    blantyre_tz = timezone(timedelta(hours=BLANTYRE_TZ_OFFSET))
    return utc_dt.astimezone(blantyre_tz)

def blantyre_to_utc(blantyre_dt: datetime) -> datetime:
    """Convert Blantyre datetime to UTC."""
    if blantyre_dt.tzinfo is None:
        blantyre_tz = timezone(timedelta(hours=BLANTYRE_TZ_OFFSET))
        blantyre_dt = blantyre_dt.replace(tzinfo=blantyre_tz)
    
    return blantyre_dt.astimezone(timezone.utc)

def format_date_for_display(dt: datetime) -> str:
    """Format datetime for display in Blantyre timezone."""
    blantyre_dt = utc_to_blantyre(dt) if dt.tzinfo else dt
    return blantyre_dt.strftime("%B %d, %Y")

def format_time_for_display(dt: datetime) -> str:
    """Format time for display in Blantyre timezone."""
    blantyre_dt = utc_to_blantyre(dt) if dt.tzinfo else dt
    return blantyre_dt.strftime("%I:%M %p")

def parse_date_string(date_str: str) -> Optional[date]:
    """Parse date string in various formats."""
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%B %d, %Y",
        "%b %d, %Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None

def get_daily_summary_time_utc() -> datetime:
    """Get the UTC time for daily summary (17:00 Blantyre time)."""
    blantyre_time = datetime.now().replace(hour=17, minute=0, second=0, microsecond=0)
    return blantyre_to_utc(blantyre_time)

def is_business_day(check_date: Optional[date] = None) -> bool:
    """Check if the given date is a business day (Monday-Friday)."""
    if check_date is None:
        check_date = get_blantyre_today()
    
    # Monday = 0, Sunday = 6
    return check_date.weekday() < 5 