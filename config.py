import os
from dotenv import load_dotenv

load_dotenv()

# LinkedIn credentials
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# Notion API
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# File paths
RESUME_BASE = "templates/resume.pdf"
RESUME_TEMPLATE_DIR = "templates/resume_templates"
COVER_LETTER_TEMPLATE_DIR = "templates/cover_letter_templates"
OUTPUT_DIR = "output"

# Other configurations
MAX_RETRIES = 3
TIMEOUT = 10
