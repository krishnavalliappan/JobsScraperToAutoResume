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
SCROLL_PAUSE_TIME = 2

# Job search settings
DEFAULT_SORT_BY = "DD"
DEFAULT_TIME_FILTER = 2  # in days
DEFAULT_EXPERIENCE_LEVEL = "2,3"
DEFAULT_DISTANCE = 25

# Logging settings
LOG_FILE = os.path.join("logs", "app.log")
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# GPT settings
GPT_MODEL_PRIMARY = "gpt-4o"
GPT_MODEL_PRIMARY = "gpt-3.5-turbo"

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
