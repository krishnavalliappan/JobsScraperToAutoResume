from operator import le
from os import read
import pandas as pd
from utilities import calculate_posted_time
from gpt import JobAnalyzer
import PyPDF2

# Class to process data

class ProcessData():
    
    def __init__(self, data):
        self.df_new = self.create_df(data)
        self.resume = self.read_pdf_resume("resume.pdf")
        print(len(self.df_new))
        self.remove_duplicates(self.df_new)
        print(len(self.df_new))
        self.add_posted_date(self.df_new)
        self.compare_df_csv()
        self.df_new.to_csv("job_application_pre_processing.csv", index=False)
        
    def compare_df_csv(self):
        old_df = pd.read_csv("job_application.csv")
        # Get the set of job_ids from old_df
        existing_job_ids = set(old_df['job_id'])

        #Remove rows from self.new_df where job_id is in existing_job_ids
        self.df_new = self.df_new[~self.df_new['job_id'].isin(existing_job_ids)]
    
    def create_df(self, data):
        return pd.DataFrame(data)
    
    def remove_duplicates(self, df):
        self.df_new = df.drop_duplicates(subset=['job_id'], keep='first')
        self.df_new = self.custom_drop_duplicates(df, 'apply_link')
    
    def custom_drop_duplicates(self, df, column):
    # Keep track of seen non-empty values
        seen = set()
    
        def keep(value):
            if value == "":
                return True
            if value not in seen:
                seen.add(value)
                return True
            return False
    
        return df[df[column].apply(keep)]
    
    def add_posted_date(self, df):
        df['posted_date'] = df['days_ago'].apply(lambda x: calculate_posted_time(x))
    
    async def analyze_job(self):
        try:
            analyzer = JobAnalyzer(self.df_new, self.resume)
            df_new, df_update = await analyzer.process_jobs()
            self.df_new = pd.concat([self.df_new, df_new], axis=1)
            self.df_new.update(df_update)
            self.append_data_csv()
        except Exception as e:
            print(f"An error occurred in pandas cancat: {str(e)}")
            
    def append_data_csv(self):
        with open('job_application.csv', 'a') as f:
            f.write('\n')
        # Now append the new data
        self.df_new.to_csv('job_application.csv', mode='a', header=False, index=False)
       
    @staticmethod
    def read_pdf_resume(file_path):
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text