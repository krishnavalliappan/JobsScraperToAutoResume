import pandas as pd
import PyPDF2
from typing import List, Dict, Any
from src.utilities import calculate_posted_time
from src.processor.gpt_processor import JobAnalyzer
from src.config import RESUME_PDF_PATH

class DataProcessor:
    def __init__(self, data: List[Dict[str, Any]], resume_path: str = RESUME_PDF_PATH):
        self.df_new = self._create_df(data)
        self.resume = self._read_pdf_resume(resume_path)
        self._preprocess_data()

    def _create_df(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        return pd.DataFrame(data)

    def _preprocess_data(self) -> None:
        self._remove_duplicates()
        self._add_posted_date()
        self._compare_with_existing_data()
        self._save_preprocessed_data()

    def _remove_duplicates(self) -> None:
        self.df_new = self.df_new.drop_duplicates(subset=['job_id'], keep='first')
        self.df_new = self._custom_drop_duplicates('apply_link')

    def _custom_drop_duplicates(self, column: str) -> pd.DataFrame:
        seen = set()
        return self.df_new[self.df_new[column].apply(lambda x: x == "" or (x not in seen and not seen.add(x)))]

    def _add_posted_date(self) -> None:
        self.df_new['posted_date'] = self.df_new['days_ago'].apply(calculate_posted_time)

    def _compare_with_existing_data(self) -> None:
        try:
            old_df = pd.read_csv("job_application.csv")
            existing_job_ids = set(old_df['job_id'])
            self.df_new = self.df_new[~self.df_new['job_id'].isin(existing_job_ids)]
        except FileNotFoundError:
            print("No existing job_application.csv found. Processing all data as new.")

    def _save_preprocessed_data(self) -> None:
        self.df_new.to_csv("job_application_pre_processing.csv", index=False)

    async def analyze_jobs(self) -> None:
        try:
            analyzer = JobAnalyzer(self.df_new, self.resume)
            df_new, df_update = await analyzer.process_jobs()
            
            self.df_new = pd.merge(self.df_new, df_new, on='job_id', how='left')
            self.df_new.update(df_update)
            
            self.df_new = self.df_new[self.df_new["job_category"] != "no match"]
            
            self._append_data_to_csv()
        except Exception as e:
            print(f"An error occurred during job analysis: {str(e)}")

    def _append_data_to_csv(self) -> None:
        try:
            with open('job_application.csv', 'a') as f:
                f.write('\n')
            self.df_new.to_csv('job_application.csv', mode='a', header=False, index=False)
        except Exception as e:
            print(f"Error appending data to CSV: {str(e)}")

    @staticmethod
    def _read_pdf_resume(file_path: str) -> str:
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                return " ".join(page.extract_text() for page in reader.pages)
        except Exception as e:
            print(f"Error reading PDF resume: {str(e)}")
            return ""

    def get_processed_data(self) -> pd.DataFrame:
        return self.df_new
