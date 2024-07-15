import math
import logging
from selenium.webdriver.common.by import By
import os
import sys
import time

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from linkedInscrapper import LinkedInScraper


# Set up logging
logging.basicConfig(filename='linkedin_search.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class LinkedIn:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.linkedin = LinkedInScraper(self.username, self.password)
        self.scraped_job_data = []

    def search_jobs_runner(self, keyword, sort_by="DD", time_filter="r604800", experience_level="2,3", distance=25, industry=None):
        try:
            result_title, no_of_results = self.linkedin.search_job(keyword, sort_by=sort_by, time_filter=time_filter, 
                                                                   experience_level=experience_level, distance=distance, industry=industry)
            
            if result_title is None or no_of_results is None:
                logging.error("Failed to retrieve search results")
                return

            logging.info(f"Search results: {result_title}, Total jobs: {no_of_results}")

            total_pages = math.ceil(no_of_results / 25)
            for page in range(total_pages):
                try:
                    self._process_page(page)
                except Exception as e:
                    logging.error(f"Error processing page {page + 1}: {str(e)}")

                if page != total_pages - 1:
                    try:
                        self.linkedin.page_clicker(page + 2)
                    except Exception as e:
                        logging.error(f"Error clicking to next page: {str(e)}")
                        break

        except Exception as e:
            logging.error(f"An error occurred in search_jobs_runner: {str(e)}")

        finally:
            if len(self.scraped_job_data) > 0:
                logging.info(f"Successfully scraped {len(self.scraped_job_data)} job listings")
            

    def _process_page(self, page):
        try:
            self.linkedin.scroll_to_bottom_element(By.CSS_SELECTOR, "div.jobs-search-results-list")
            ul_element = self.linkedin.driver.find_element(By.CSS_SELECTOR, "ul.scaffold-layout__list-container")
            li_elements = ul_element.find_elements(By.CSS_SELECTOR, "li.jobs-search-results__list-item")
            
            logging.info(f"Found {len(li_elements)} job listings on page {page + 1}")

            for i, li in enumerate(li_elements):
                try:
                    job_data = self._process_job_listing(li, i)
                    self.scraped_job_data.append(job_data)
                except Exception as e:
                    logging.error(f"Error processing job listing {i + 1} on page {page + 1}: {str(e)}")
                
                try:
                    self.linkedin.scroll_to_bottom_element(By.CSS_SELECTOR, "div.jobs-search-results-list", scroll_full=False)
                except Exception as e:
                    logging.warning(f"Error scrolling after processing job {i + 1}: {str(e)}") 

        except Exception as e:
            logging.error(f"Error processing page {page + 1}: {str(e)}")

    def _process_job_listing(self, li, index):
        try:
            div_clickable = li.find_element(By.CSS_SELECTOR, "div.job-card-container--clickable")
            div_clickable.click()
        except Exception as e:
            logging.warning(f"Couldn't click div.job-card-container--clickable for job {index + 1}, trying to click li: {str(e)}")
            li.click()

        try:
            job_data = self.linkedin.crab_job_details()
            logging.info(f"Successfully scraped job {index + 1}: {job_data.get('job_position_title', 'Unknown Title')}")
            
            return job_data
            
        except Exception as e:
            logging.error(f"Error scraping details for job {index + 1}: {str(e)}")