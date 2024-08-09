# from g4f.client import Client
# import os.path
# from g4f.cookies import set_cookies_dir, read_cookie_files
# from g4f.Provider import (Liaobots)
# import g4f

# import g4f.debug

# g4f.debug.logging = True
# cookies_dir = os.path.join(os.path.dirname(__file__), "har_and_cookies")
# set_cookies_dir(cookies_dir)
# read_cookie_files(cookies_dir)


# client = Client(Liaobots)
# response = client.chat.completions.create(
#     model=g4f.models.gpt_4o,
#     messages=[{"role": "user", "content": "Tell me about Coveo company for my interview"}],
# )              
# print(response.choices[0].message.content)

# from LinkedIn.linkedIn import LinkedIn

# linkedin = LinkedIn("krishnavalliappan02@gmail.com", "YE$35A!GJjn@AQ!3")
# linkedin.search_jobs_runner("data analyst", time_filter=2)
# from datamanger import DataManager

# dm = DataManager("localhost", "root", "welcome123", "linkedin_data")

# # Connect to the database (creates it if it doesn't exist)
# dm.connect()

# # Execute a sample query (e.g., create a table)
# # dm.execute_query("""
# #     CREATE TABLE IF NOT EXISTS users (
# #         id INT AUTO_INCREMENT PRIMARY KEY,
# #         name VARCHAR(255),
# #         email VARCHAR(255)
# #     )
# # """)

# # Disconnect when done
# dm.disconnect()

# In main.py:
# from processData import ProcessData
# import asyncio
# from linkedin.linkedIn import LinkedIn
# from ResumeManager.resumeManager import ResumeManager
# import os
# import pandas as pd
# from dotenv import load_dotenv
# from notion_manager import NotionManager

# load_dotenv()

# async def main():
#     linkedin_email = os.environ.get('LINKEDIN_EMAIL')
#     linkedin_password = os.environ.get('LINKEDIN_PASSWORD')
#     database_id = "7585377689d14a70bce0e38935403a1b"
    
#     if not linkedin_email or not linkedin_password:
#         raise ValueError("LinkedIn credentials not set in environment variables")

#     try:
#         linkedin = LinkedIn(linkedin_email, linkedin_password)
#         linkedin.search_jobs_runner("Data Analyst", time_filter=1)
#         data = linkedin.scraped_job_data
#         # data = pd.read_csv("job_application_pre_processing.csv")
#         process_data = ProcessData(data)
#         await process_data.analyze_job()
#         # create resumes and cover_letters
#         new_df = process_data.df_new
#         ResumeManager(new_df)
#         notion = NotionManager(database_id=database_id)
#         notion.one_way_sync(new_df)
#     except Exception as e:
#         print(f"An error occurred: {e}")

# if __name__ == "__main__":
#     asyncio.run(main())

from src.scraper_linkedin import LinkedIn
from src.processor import DataProcessor
import logging
import asyncio
import pandas as pd
from src.document_generator import ResumeManager
from src.notion_integration import NotionManager
from src.utilities import duration_to_seconds

async def main():
    logging.basicConfig(
      filename='linkedin_search.log', 
      level=logging.INFO,
      format='%(asctime)s - %(levelname)s - %(message)s')
    
    linkedin = LinkedIn()

    linkedin.search_jobs_runner("full stack developer", experience_level="2", time_filter="1 day")

    scraped_data = linkedin.get_scraped_data()
    # scraped_data = pd.read_csv("job_application_pre_processing.csv")
    data_processor = DataProcessor(scraped_data)
    await data_processor.analyze_jobs()
    data = data_processor.get_processed_data()
    ResumeManager(data)
    NotionManager(data)
    
if __name__ == "__main__":
  asyncio.run(main())