import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LinkedIn credentials
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# Notion settings
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# File paths
RESUME_PDF_PATH = os.path.join("templates", "resume.pdf")
RESUME_TEMPLATES_DIR = os.path.join("templates")
OUTPUT_RESUMES_DIR = os.path.join("output", "resumes")

# LinkedIn scraper settings
COOKIE_FILE = "cookies/linkedin_cookies.pkl"

# Job search settings
DEFAULT_SORT_BY = "DD"
DEFAULT_TIME_FILTER = "1 day"  # in days
DEFAULT_EXPERIENCE_LEVEL = "2,3"
DEFAULT_DISTANCE = 25
"""
LinkedIn GeoID Configuration

The `geo_id` parameter is used to filter job listings by geographic location in LinkedIn's job search.
Default is set to Canada (geo_id: 101174742).

To customize the geo_id for a different location:

1. Open an incognito/private browsing window to avoid personalized results.
2. Navigate to LinkedIn's job search page (https://www.linkedin.com/jobs/).
3. In the location filter input, enter your desired region.
4. Select the appropriate option from the autocomplete dialog.
5. After the results load, examine the URL in the address bar.
6. Locate the `geoId` parameter in the URL. For example:
   https://www.linkedin.com/jobs/search?keywords=&location=Canada&geoId=101174742&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0

In this example, the geo_id for Canada is 101174742.

Note: LinkedIn may update their URL structure or geo_id values over time.
Always verify the current format and values before use.
"""
DEFAULT_GEO_ID = "101174742"
DEFAULT_JOB_FUNCTION = "it%2Canls"
DEFAULT_INDUSTRY = None  

# Logging settings
LOG_FILE = os.path.join("logs", "app.log")
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# GPT settings
GPT_MODEL_PRIMARY = "gpt-4o-mini"
GPT_MODEL_SECONDARY = "gpt-3.5-turbo"

# Proxy settings
PROXY_URL = "https://free-proxy-list.net/"

# Notion schema
NOTION_SCHEMA = {
    "job_position_title": {
        "type": "title",
        "notion_prop_name": "Job Role"
    },
    "job_id": {
        "type": "number",
        "notion_prop_name": "Job ID"
    },
    "job_position_link": {
        "type": "url",
        "notion_prop_name": "Job Link"
    },
    "company_name": {
        "type": "select",
        "notion_prop_name": "Company"
    },
    "location": {
        "type": "select",
        "notion_prop_name": "Location"
    },
    "days_ago": {
        "type": "rich_text",
        "notion_prop_name": "Posted"
    },
    "no_of_applicants": {
        "type": "number",
        "notion_prop_name": "Applicants"
    },
    "salary": {
        "type": "rich_text",
        "notion_prop_name": "Salary"
    },
    "workplace": {
        "type": "select",
        "notion_prop_name": "Workplace"
    },
    "job_type": {
        "type": "select",
        "notion_prop_name": "Job Type"
    },
    "experience_level": {
        "type": "select",
        "notion_prop_name": "Experience Level"
    },
    "industry": {
        "type": "select",
        "notion_prop_name": "Industry"
    },
    "is_easy_apply": {
        "type": "checkbox",
        "notion_prop_name": "Easy Apply"
    },
    "apply_link": {
        "type": "url",
        "notion_prop_name": "Apply Link"
    },
    "posted_date": {
        "type": "date",
        "notion_prop_name": "Posted Date"
    },
    "top_skills": {
        "type": "multi_select",
        "notion_prop_name": "Top Skills"
    },
    "job_category": {
        "type": "select",
        "notion_prop_name": "Job Category"
    }
}

# Add any other configuration variables here
