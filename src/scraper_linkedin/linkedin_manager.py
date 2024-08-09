import math
import logging
from typing import List, Dict, Any, Optional
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import time
from src.config import LINKEDIN_EMAIL, LINKEDIN_PASSWORD

from .linkedin_scraper import LinkedInScraper

class LinkedIn:
    """
    A class to manage LinkedIn job searches and data extraction.
    """

    def __init__(self):
        """
        A class to manage LinkedIn job searches and data extraction.
        """
        self.logger = logging.getLogger(__name__)
        self.linkedin = LinkedInScraper(LINKEDIN_EMAIL,LINKEDIN_PASSWORD)
        self.scraped_job_data: List[Dict[str, Any]] = []

    def search_jobs_runner(self, keyword: str, **kwargs) -> None:
        """
        Run a job search and process the results.

        Args:
            keyword (str): The job search keyword.
            **kwargs: Additional search parameters.
        """
        try:
            result_title, no_of_results = self.linkedin.search_job(keyword, **kwargs)
            
            if result_title is None or no_of_results is None:
                self.logger.error("Failed to retrieve search results")
                return

            self.logger.info(f"Search results: {result_title}, Total jobs: {no_of_results}")

            total_pages = math.ceil(no_of_results / 25)
            for page in range(total_pages):
                try:
                    self._process_page(page)
                except Exception as e:
                    self.logger.error(f"Error processing page {page + 1}: {str(e)}")

                if page != total_pages - 1:
                    try:
                        self.linkedin.page_clicker(page + 2)
                    except Exception as e:
                        self.logger.error(f"Error clicking to next page: {str(e)}")
                        break

        except Exception as e:
            self.logger.error(f"An error occurred in search_jobs_runner: {str(e)}")

        finally:
            if self.scraped_job_data:
                self.logger.info(f"Successfully scraped {len(self.scraped_job_data)} job listings")
            self.linkedin.driver.quit()

    def _process_page(self, page: int) -> None:
        """
        Process a single page of job listings.

        Args:
            page (int): The page number being processed.
        """
        try:
            self.linkedin.scroll_to_bottom_element(By.CSS_SELECTOR, "div.jobs-search-results-list")
            ul_element = self.linkedin.driver.find_element(By.CSS_SELECTOR, "ul.scaffold-layout__list-container")
            li_elements = ul_element.find_elements(By.CSS_SELECTOR, "li.jobs-search-results__list-item")
            
            self.logger.info(f"Found {len(li_elements)} job listings on page {page + 1}")

            for i, li in enumerate(li_elements):
                try:
                    job_data = self._process_job_listing(li, i)
                    if job_data:
                        self.scraped_job_data.append(job_data)
                except Exception as e:
                    self.logger.error(f"Error processing job listing {i + 1} on page {page + 1}: {str(e)}")
                
                self._scroll_after_processing(i)

        except WebDriverException as e:
            self.logger.error(f"WebDriver error while processing page {page + 1}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error processing page {page + 1}: {str(e)}")

    def _process_job_listing(self, li_element: Any, index: int) -> Optional[Dict[str, Any]]:
        """
        Process an individual job listing.

        Args:
            li_element: The WebElement representing the job listing.
            index (int): The index of the job listing on the page.

        Returns:
            Optional[Dict[str, Any]]: The scraped job data, or None if an error occurred.
        """
        try:
            self._click_job_listing(li_element)
            job_data = self.linkedin.crab_job_details()
            self.logger.info(f"Successfully scraped job {index + 1}: {job_data.get('job_position_title', 'Unknown Title')}")
            return job_data
        except Exception as e:
            self.logger.error(f"Error scraping details for job {index + 1}: {str(e)}")
            return None

    def _click_job_listing(self, li_element: Any) -> None:
        """
        Click on a job listing to view its details.

        Args:
            li_element: The WebElement representing the job listing.
        """
        try:
            div_clickable = li_element.find_element(By.CSS_SELECTOR, "div.job-card-container--clickable")
            div_clickable.click()
        except Exception:
            self.logger.warning("Couldn't click div.job-card-container--clickable, trying to click li")
            li_element.click()

    def _scroll_after_processing(self, index: int) -> None:
        """
        Scroll the page after processing a job listing.

        Args:
            index (int): The index of the job listing that was just processed.
        """
        try:
            self.linkedin.scroll_to_bottom_element(By.CSS_SELECTOR, "div.jobs-search-results-list", scroll_full=False)
        except Exception as e:
            self.logger.warning(f"Error scrolling after processing job {index + 1}: {str(e)}")

    def get_scraped_data(self) -> List[Dict[str, Any]]:
        """
        Get the scraped job data.

        Returns:
            List[Dict[str, Any]]: The list of scraped job data.
        """
        return self.scraped_job_data


