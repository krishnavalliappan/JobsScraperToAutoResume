from urllib.parse import urlencode, quote_plus
from datetime import datetime, timedelta
import re

def calculate_posted_time(time_ago_string):
    try:
        current_time = datetime.now()
        
        # Extract number and unit from the input string
        match = re.match(r'(\d+)\s+(\w+)\s+ago', time_ago_string)
        if not match:
            raise ValueError("Invalid input format")
        
        number, unit = int(match.group(1)), match.group(2).lower()
        
        # Define time units
        units = {
            'second': timedelta(seconds=1),
            'minute': timedelta(minutes=1),
            'hour': timedelta(hours=1),
            'day': timedelta(days=1),
            'week': timedelta(weeks=1),
            'month': timedelta(days=30),  # Approximation
            'year': timedelta(days=365)  # Approximation
        }
        
        # Handle plural forms
        if unit.endswith('s'):
            unit = unit[:-1]
        
        if unit not in units:
            raise ValueError("Invalid time unit")
        
        # Calculate the posted time
        posted_time = current_time - (units[unit] * number)
        
        return posted_time
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return datetime.now()

def generate_linkedin_job_search_url(keyword, sort_by="DD", time_filter=2, experience_level="2,3", distance=25, industry=None):
    # industry: LinkedIn uses a hierarchical system for industries.
    # Examples include "4" (Computer Software), "6" (Internet),
    # "51" (Information Technology and Services)
    # Refer to LinkedIn's current industry taxonomy for a complete list

    # sortBy: Options include:
    # "R" (Most relevant), "DD" (Most recent), "PA" (Most viewed)

    # time_filter: Options include:
    # defualts to last 2 days, you can give how many days back you want to search

    # experience_level: Options include:
    # "1" (Internship), "2" (Entry level), "3" (Associate),
    # "4" (Mid-Senior level), "5" (Director), "6" (Executive)
    # Use comma-separated values for multiple levels, e.g., "2,3"

    # distance: Numeric value representing the search radius in miles or kilometers
    
    time_filter = "r" + str(time_filter*86400)  # Convert days to seconds
    
    base_url = "https://www.linkedin.com/jobs/search/?"
    
    params = {
        "keywords": keyword,
        "f_F": "it%2Canls",
        "f_I": industry,
        "sortBy": sort_by,
        "f_TPR": time_filter,
        "f_E": experience_level,
        "distance": distance,
        "geoId": "101174742",  # You may want to make this parameter customizable
        "origin": "JOB_SEARCH_PAGE_JOB_FILTER",
        "refresh": "false",
        "spellCorrectionEnabled": "true"
    }
    
    # Remove any None values from the params
    params = {k: v for k, v in params.items() if v is not None}
    
    # Encode the parameters
    encoded_params = urlencode(params, quote_via=quote_plus)
    
    # Combine the base URL with the encoded parameters
    full_url = base_url + encoded_params
    
    return full_url