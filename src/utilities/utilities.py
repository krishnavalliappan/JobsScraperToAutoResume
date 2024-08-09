import re
from datetime import datetime, timedelta
from urllib.parse import urlencode, quote_plus
import pytz

from src.config import (
    DEFAULT_SORT_BY, DEFAULT_EXPERIENCE_LEVEL, DEFAULT_DISTANCE,
    DEFAULT_TIME_FILTER, DEFAULT_GEO_ID, DEFAULT_JOB_FUNCTION, DEFAULT_INDUSTRY
)

def calculate_posted_time(time_ago_string):
    """Calculate the posted time based on a 'time ago' string."""
    try:
        current_time = datetime.now()
        match = re.match(r'(\d+)\s+(\w+)\s+ago', time_ago_string)
        if not match:
            raise ValueError("Invalid input format")

        number, unit = int(match.group(1)), match.group(2).lower().rstrip('s')

        units = {
            'second': timedelta(seconds=1),
            'minute': timedelta(minutes=1),
            'hour': timedelta(hours=1),
            'day': timedelta(days=1),
            'week': timedelta(weeks=1),
            'month': timedelta(days=30),  # Approximation
            'year': timedelta(days=365)  # Approximation
        }

        if unit not in units:
            raise ValueError("Invalid time unit")

        return current_time - (units[unit] * number)

    except Exception as e:
        print(f"An error occurred in calculate_posted_time: {str(e)}")
        return datetime.now()

def convert_to_iso_time(date_string, local_timezone='America/New_York'):
    """Convert a local datetime string to ISO 8601 format in UTC."""
    local_time = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S.%f")
    local_tz = pytz.timezone(local_timezone)
    local_time_with_tz = local_tz.localize(local_time)
    utc_time = local_time_with_tz.astimezone(pytz.UTC)
    return utc_time.isoformat()

def duration_to_seconds(duration_string):
    """Convert a duration string to seconds."""
    time_units = {
        'second': 1,
        'minute': 60,
        'hour': 3600,
        'day': 86400,
        'week': 604800
    }
    default_seconds = 86400  # 1 day in seconds

    total_seconds = 0
    parts = re.findall(r'(\d+)\s*(\w+)', duration_string)
    
    for number, unit in parts:
        number = int(number)
        unit = unit.lower().rstrip('s')
        if unit in time_units:
            total_seconds += number * time_units[unit]

    if total_seconds == 0:
        total_seconds = default_seconds

    return f"r{str(total_seconds)}"


def generate_linkedin_job_search_url(
    keyword,
    sort_by=DEFAULT_SORT_BY,
    time_filter=DEFAULT_TIME_FILTER,
    experience_level=DEFAULT_EXPERIENCE_LEVEL,
    distance=DEFAULT_DISTANCE,
    industry=DEFAULT_INDUSTRY,
    geo_id=DEFAULT_GEO_ID,
    job_function=DEFAULT_JOB_FUNCTION
):
    """Generate a LinkedIn job search URL with the given parameters."""
    time_filter = duration_to_seconds(time_filter)

    params = {
        "keywords": keyword,
        "sortBy": sort_by,
        "f_TPR": time_filter,
        "f_E": experience_level,
        "distance": distance,
        "geoId": geo_id,
        "origin": "JOB_SEARCH_PAGE_JOB_FILTER",
        "refresh": "false",
        "spellCorrectionEnabled": "true"
    }

    if industry:
        params["f_I"] = industry

    # Remove any None values from the params
    params = {k: v for k, v in params.items() if v is not None}

    base_url = "https://www.linkedin.com/jobs/search/?"
    encoded_params = urlencode(params, quote_via=quote_plus)
    
    # Add the job_function parameter separately without encoding
    if job_function:
        encoded_params += f"&f_F={job_function}"
    if industry:
        encoded_params += f"&f_I={industry}"

    return base_url + encoded_params