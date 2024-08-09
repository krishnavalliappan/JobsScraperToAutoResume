import os
from typing import Dict, Any, List
from notion_client import Client
import pandas as pd
from dotenv import load_dotenv
from src.config import NOTION_API_KEY, NOTION_SCHEMA, NOTION_DATABASE_ID

class NotionManager:
    def __init__(self, df,  database_id: str = NOTION_DATABASE_ID):
        self.notion = self._initialize_notion_client()
        self.df = df
        self.database_id = database_id
        self.sync_to_notion(self.df)

    @staticmethod
    def _initialize_notion_client() -> Client:
        load_dotenv()
        api_key = os.getenv("NOTION_API_KEY", NOTION_API_KEY)
        if not api_key:
            raise ValueError("Notion API key not found in environment variables or config")
        return Client(auth=api_key)

    def create_property(self, property_name: str, property_type: str) -> None:
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

    def sync_to_notion(self, df: pd.DataFrame) -> None:
        for _, row in df.iterrows():
            properties = self._prepare_properties(row)
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

    def _prepare_properties(self, row: pd.Series) -> Dict[str, Any]:
        properties = {}
        for col, prop_data in NOTION_SCHEMA.items():
            notion_prop_name = prop_data["notion_prop_name"]
            notion_type = prop_data["type"]
            value = row[col]

            properties[notion_prop_name] = self._format_property(notion_type, value)
        return properties

    @staticmethod
    def _format_property(notion_type: str, value: Any) -> Dict[str, Any]:
        if notion_type == "title":
            return {"title": [{"text": {"content": str(value)}}]}
        elif notion_type == "rich_text":
            return {"rich_text": [{"text": {"content": str(value)}}]}
        elif notion_type == "number":
            return {"number": float(value) if pd.notna(value) else None}
        elif notion_type == "select":
            return {"select": {"name": str(value).replace(",", "-")}}
        elif notion_type == "multi_select":
            return {"multi_select": [{"name": item.strip()} for item in str(value).split(',')]}
        elif notion_type == "date":
            return {"date": {"start": str(value), "time_zone": "America/Montreal"}}
        elif notion_type == "checkbox":
            return {"checkbox": bool(value)}
        elif notion_type == "url":
            return {"url": str(value)}
        else:
            raise ValueError(f"Unsupported Notion property type: {notion_type}")

    def add_detailed_content(self, page_id: str, row: pd.Series) -> None:
        blocks = self._create_content_blocks(row)
        self.notion.blocks.children.append(page_id, children=blocks)

    @staticmethod
    def _create_content_blocks(row: pd.Series) -> List[Dict[str, Any]]:
        blocks = []
        sections = [
            ("Job Description", row['job_description']),
            ("Why This Company", row['why_this_company']),
            ("Why Me", row['why_me'])
        ]

        for title, content in sections:
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": title}}]
                }
            })
            blocks.extend(NotionManager._create_paragraph_blocks(content))

        return blocks

    @staticmethod
    def _create_paragraph_blocks(content: str) -> List[Dict[str, Any]]:
        blocks = []
        while content:
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

    def one_way_sync(self, df: pd.DataFrame) -> None:
        self.sync_to_notion(df)

if __name__ == "__main__":
    # Example usage
    pass
