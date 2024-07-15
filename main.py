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