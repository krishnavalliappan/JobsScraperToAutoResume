import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium_stealth import stealth
import pickle
import os
import sys
import logging
import re
import random
from utilities import generate_linkedin_job_search_url

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Set up logging
logging.basicConfig(filename='linkedin_scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def create_stealth_driver():
    options = Options()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)
    
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    
    return driver

class LinkedInScraper:
    def __init__(self, username, password, cookie_file="linkedin_cookies.pkl"):
        self.username = username
        self.password = password
        self.cookie_file = cookie_file
        self.driver = create_stealth_driver()
        self.initial_start()
    
    def initial_start(self):
        try:
            if os.path.exists(self.cookie_file):
                self.driver.get("https://www.linkedin.com")
                self.load_cookies()
                self.driver.refresh()
                
                if "login" in self.driver.current_url:
                    logging.info("Cookies expired, logging in again")
                    self.login_to_linkedin()
                else:
                    logging.info("Successfully logged in using cookies")
            else:
                self.login_to_linkedin()
            
            self.save_cookies()
            
        except Exception as e:
            logging.error(f"An error occurred during initial start: {str(e)}")
    
    def login_to_linkedin(self):
        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(random.uniform(2, 8))
            
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.send_keys(self.username)
            
            time.sleep(random.uniform(1, 4))
            
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            
            time.sleep(random.uniform(1, 2))
            
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "global-nav"))
            )
            
            logging.info("Successfully logged in to LinkedIn")
        except Exception as e:
            logging.error(f"Error during login: {str(e)}")
            raise
        
    def save_cookies(self):
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookie_file, "wb") as f:
                pickle.dump(cookies, f)
            logging.info(f"Saved cookies to {self.cookie_file}")
        except Exception as e:
            logging.error(f"Error saving cookies: {str(e)}")
    
    def load_cookies(self):
        try:
            if os.path.exists(self.cookie_file):
                with open(self.cookie_file, "rb") as f:
                    cookies = pickle.load(f)
                    for cookie in cookies:
                        self.driver.add_cookie(cookie)
                logging.info(f"Loaded cookies from {self.cookie_file}")
            else:
                logging.warning(f"Cookie file {self.cookie_file} not found")
        except Exception as e:
            logging.error(f"Error loading cookies: {str(e)}")
    
    def scroll_to_bottom_page(self):
        try:
            SCROLL_PAUSE_TIME = 2
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(SCROLL_PAUSE_TIME)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
        except Exception as e:
            logging.error(f"Error during scrolling: {str(e)}")
    
    def scroll_to_bottom_element(self, by, element_value, scroll_full=True):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by, element_value))
            )
            
            last_height = self.driver.execute_script("return arguments[0].scrollHeight;", element)
            
            while True:
                if scroll_full:
                    self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", element)
                else:
                    visible_height = self.driver.execute_script("return arguments[0].clientHeight;", element)
                    self.driver.execute_script(f"arguments[0].scrollBy(0, {visible_height * 0.32});", element)
                
                time.sleep(2)
                
                new_height = self.driver.execute_script("return arguments[0].scrollHeight;", element)
                
                if new_height == last_height:
                    break
                
                last_height = new_height
                
                if not scroll_full:
                    break

            ActionChains(self.driver).move_to_element(element).perform()
        except Exception as e:
            logging.error(f"Error during element scrolling: {str(e)}")
    
    def search_job(self, keyword, **kwargs):
        try:
            url = generate_linkedin_job_search_url(keyword, **kwargs)
            self.driver.get(url)
            logging.info(f"Searching for jobs with keyword: {keyword}")
            result_title = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "results-list__title"))
            ).text
            no_of_results = int(self.driver.find_element(By.CSS_SELECTOR, "div.jobs-search-results-list__subtitle span").text.split()[0])    
            logging.info(f"Search results loaded successfully for {result_title} with {no_of_results} results")
            
            return result_title, no_of_results
        except Exception as e:
            logging.error(f"Error during job search: {str(e)}")
            return None

    def page_clicker(self, page_no):
        try:
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[@aria-label='Page {page_no}']"))
            )
            button.click()
            time.sleep(5)
            logging.info(f"Successfully clicked the 'Page {page_no}' button")
        except Exception as e:
            logging.error(f"Error clicking page button: {str(e)}")
            
    def get_job_id(self, href):
        try:
            return href.split("/")[5]
        except Exception as e:
            logging.error(f"Error extracting job ID: {str(e)}")
            return None
    
    def remove_characters(self, text):
        try:
            number = re.findall(r'\d+', text)
            return int(number[0]) if number else 0
        except Exception as e:
            logging.error(f"Error removing characters: {str(e)}")
            return 0
    
    def extract_job_details(self, job_element):
        salary = workplace = job_type = experience_level = None
        try:
            salary_element = job_element.find_element(By.CSS_SELECTOR, "span > span:not([class])")
            children = salary_element.find_elements(By.XPATH, "./*")
            salary = salary_element.text.strip() if len(children) == 0 else None
        except Exception as e:
            logging.error(f"Error extracting salary: {str(e)}")

        try:
            span_models = job_element.find_elements(By.XPATH, 
                ".//span[contains(@class, 'ui-label ui-label--accent-3 text-body-small')] | " +
                ".//span[contains(@class, 'job-details-jobs-unified-top-card__job-insight-view-model-secondary')]")
            
            for element in span_models:
                text = element.text.strip() if len(element.find_elements(By.XPATH, "./*")) == 0 else element.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']").text.strip()
                
                if text in ['Full-time', 'Part-time', 'Contract', 'Temporary', 'Internship', "Other"]:
                    job_type = text
                elif text in ['Entry level', 'Associate', 'Mid-Senior level', 'Director', 'Executive']:
                    experience_level = text
                elif text in ['Remote', 'Hybrid', "On-site"]:
                    workplace = text
                
        except Exception as e:
            logging.error(f"Error extracting job details: {str(e)}")

        return salary, workplace, job_type, experience_level
        
    def apply_link_finder(self, element):
        is_easy_apply = False
        apply_link = None
        try:
            button_element = element.find_element(By.CSS_SELECTOR, "div.jobs-apply-button--top-card button")
            if button_element.find_element(By.TAG_NAME, "span").text.strip() == "Easy Apply":
                is_easy_apply = True
            else:
                button_element.click()
                time.sleep(2)
                
                if len(self.driver.window_handles) > 1:
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    apply_link = self.driver.current_url
                    self.driver.close()
                    time.sleep(4)
                    self.driver.switch_to.window(self.driver.window_handles[0])
        except Exception as e:
            logging.error(f"Error finding apply link: {str(e)}")
        
        return is_easy_apply, apply_link
                
    def extract_industry(self, element):
        try:
            industry_row_span = element.find_elements(By.CSS_SELECTOR, "li.job-details-jobs-unified-top-card__job-insight")[1].find_element(By.CSS_SELECTOR, "span").text
            if "·" in industry_row_span:
                 return industry_row_span.split("·")[1].strip()
            elif "employees" not in industry_row_span:
                return industry_row_span.strip()
        except Exception as e:
            logging.error(f"Error extracting industry: {str(e)}")
        return None
        
    def crab_job_details(self):
        job_data = {
            'job_position_title': None,
            'job_id': None,
            'job_position_link': None,
            'company_logo': None,
            'company_name': None,
            'location': None,
            'days_ago': None,
            'no_of_applicants': None,
            'salary': None,
            'workplace': None,
            'job_type': None,
            'experience_level': None,
            'industry': None,
            'is_easy_apply': False,
            'apply_link': None,
            'job_description': None
        }

        try:
            time.sleep(random.uniform(2, 8))
            job_details = self.driver.find_element(By.CSS_SELECTOR, "div.jobs-search__job-details--wrapper")

            # Job position, job id, job link
            try:
                job_position_element = job_details.find_element(By.CSS_SELECTOR, "h1[class*='t-24 t-bold'] a")
                job_data['job_position_title'] = job_position_element.text
                job_data['job_position_link'] = job_position_element.get_attribute("href")
                job_data['job_id'] = self.get_job_id(job_data['job_position_link'])
            except Exception as e:
                logging.error(f"Error extracting job position details: {str(e)}")

            # Company name, image
            try:
                job_data['company_logo'] = job_details.find_element(By.CSS_SELECTOR, "div.flex-1 a.app-aware-link img").get_attribute('src')
                job_data['company_name'] = job_details.find_element(By.CSS_SELECTOR, "div.job-details-jobs-unified-top-card__company-name a.app-aware-link").text
            except Exception as e:
                logging.error(f"Error extracting company details: {str(e)}")

            # Location, posted ago, no_of_applicants
            try:
                primary_description_element = job_details.find_elements(By.CSS_SELECTOR, "div.job-details-jobs-unified-top-card__primary-description-container div span.tvm__text")
                job_data['location'] = primary_description_element[0].text if len(primary_description_element) > 0 else None
                job_data['days_ago'] = primary_description_element[2].find_element(By.CSS_SELECTOR, "span:not([class])").text if len(primary_description_element) > 2 else None
                job_data['no_of_applicants'] = self.remove_characters(primary_description_element[4].text) if len(primary_description_element) > 4 else None
            except Exception as e:
                logging.error(f"Error extracting job metadata: {str(e)}")

            # Job details (salary, workplace, job_type, experience_level)
            try:
                highlight_element = job_details.find_element(By.CSS_SELECTOR, "li.job-details-jobs-unified-top-card__job-insight--highlight")
                job_data['salary'], job_data['workplace'], job_data['job_type'], job_data['experience_level'] = self.extract_job_details(highlight_element)
            except Exception as e:
                logging.error(f"Error extracting job details: {str(e)}")

            # Industry
            try:
                job_data['industry'] = self.extract_industry(job_details)
            except Exception as e:
                logging.error(f"Error extracting industry: {str(e)}")

            # Apply link and easy apply status
            try:
                job_data['is_easy_apply'], job_data['apply_link'] = self.apply_link_finder(job_details)
            except Exception as e:
                logging.error(f"Error extracting apply link: {str(e)}")

            # Job description
            try:
                job_data['job_description'] = job_details.find_element(By.CSS_SELECTOR, "article.jobs-description__container").text.replace('\n', ' ')
            except Exception as e:
                logging.error(f"Error extracting job description: {str(e)}")

        except Exception as e:
            logging.error(f"Major error in crab_job_details: {str(e)}")

        return job_data
