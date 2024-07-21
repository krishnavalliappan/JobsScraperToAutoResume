import os
from notion_client import Client
import pandas as pd
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Get Notion API key from environment variables
NOTION_API_KEY = os.getenv("NOTION_API_KEY")

notion_schema = {
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

class NotionManager:
    def __init__(self, database_id):
        self.notion = Client(auth=NOTION_API_KEY)
        self.database_id = database_id

    def create_property(self, property_name, property_type):
        """Create a new property in the Notion database"""
        try:
            self.notion.databases.update(
                database_id=self.database_id,
                properties={
                    property_name: {
                        "type": property_type,
                        property_type: {}
                    }
                }
            )
            print(f"Property '{property_name}' of type '{property_type}' created successfully.")
        except Exception as e:
            print(f"Error creating property: {e}")

    def sync_to_notion(self, df):
        """Sync DataFrame to Notion database"""
        for _, row in df.iterrows():
            properties = {}
            for col, prop_data in notion_schema.items():
                notion_prop_name = prop_data["notion_prop_name"]
                notion_type = prop_data["type"]
                value = row[col]

                if notion_type == "title":
                    properties[notion_prop_name] = {"title": [{"text": {"content": str(value)}}]}
                elif notion_type == "rich_text":
                    properties[notion_prop_name] = {"rich_text": [{"text": {"content": str(value)}}]}
                elif notion_type == "number":
                    properties[notion_prop_name] = {"number": float(value) if pd.notna(value) else None}
                elif notion_type == "select":
                    properties[notion_prop_name] = {"select": {"name": str(value).replace(",", "-")}}
                elif notion_type == "multi_select":
                    properties[notion_prop_name] = {"multi_select": [{"name": item.strip()} for item in str(value).split(',')]}
                elif notion_type == "date":
                    properties[notion_prop_name] = {"date": {"start": str(value), "time_zone": "America/Montreal"}}
                elif notion_type == "checkbox":
                    properties[notion_prop_name] = {"checkbox": bool(value)}
                elif notion_type == "url":
                    properties[notion_prop_name] = {"url": str(value)}

            try:
                page = self.notion.pages.create(
                    parent={"database_id": self.database_id},
                    properties=properties,
                    icon={"type": "external", "external": {"url": row['company_logo']}}
                )
                self.add_detailed_content(page["id"], row)
                print(f"Row added successfully: {row['job_id']}")
            except Exception as e:
                print(f"Error adding row: {row['job_id']}. Error: {e}")

    def add_detailed_content(self, page_id, row):
        """Add job_description, why_me, and why_this_company as blocks inside the page"""
        
        def create_paragraph_blocks(content):
            blocks = []
            while len(content) > 0:
                block_content = content[:2000]
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": block_content}}]
                    }
                })
                content = content[2000:]
            return blocks

        blocks = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Job Description"}}]
                }
            },
        ]
        blocks.extend(create_paragraph_blocks(row['job_description']))

        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "Why This Company"}}]
            }
        })
        blocks.extend(create_paragraph_blocks(row['why_this_company']))

        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "Why Me"}}]
            }
        })
        blocks.extend(create_paragraph_blocks(row['why_me']))

        self.notion.blocks.children.append(page_id, children=blocks)

    def one_way_sync(self, df):
        """Perform one-way sync from DataFrame to Notion"""
        # Create properties if they don't exist
        # for prop_name, prop_data in notion_schema.items():
        #     self.create_property(prop_data["notion_prop_name"], prop_data["type"])

        # Sync data to Notion
        self.sync_to_notion(df)

# def main():
#     # Initialize NotionManager with your database ID
#     database_id = "7585377689d14a70bce0e38935403a1b"
#     notion_manager = NotionManager(database_id)

#     # # Read CSV and convert to DataFrame
#     df = pd.read_csv("job_data.csv")

#     # # Perform one-way sync
#     notion_manager.one_way_sync(df)

# if __name__ == "__main__":
#     main()
