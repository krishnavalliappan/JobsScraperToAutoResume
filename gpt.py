import json
import asyncio
from enum import Enum
from typing import List, Optional, Dict, Tuple, Any
from weakref import proxy
from pydantic import BaseModel, Field
from langchain.llms.base import LLM
import g4f
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from g4f.client import Client
from g4f.cookies import set_cookies_dir, read_cookie_files
import os
import re
import PyPDF2
import pandas as pd
from Utilities.proxies import ProxyRotator
from g4f.Provider import You, Liaobots, ChatgptAi, Bing, RetryProvider

proxy_rotator = ProxyRotator()

g4f.debug.logging = True
cookies_dir = os.path.join(os.path.dirname(__file__), "har_and_cookies")
set_cookies_dir(cookies_dir)
read_cookie_files(cookies_dir)


class EducationalLLM(LLM):
    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(self, prompt: str, stop: Optional[List[str]] = None, run_manager=None, **kwargs) -> str:
        max_retries = 2
        for attempt in range(max_retries):
            try:
                client = Client(proxies=proxy_rotator.get_proxy())
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                )
                out = response.choices[0].message.content
                if stop:
                    stop_indexes = (out.find(s) for s in stop if s in out)
                    min_stop = min(stop_indexes, default=-1)
                    if min_stop > -1:
                        out = out[:min_stop]
                print("with proxy success")
                return out
            except Exception as e:
                print(f"Attempt {attempt + 1} failed with proxy: {str(e)}")
                proxy_rotator.remove_current_proxy()
                if not proxy_rotator.proxies:
                    proxy_rotator.refresh_proxies()                  
        # If all proxy attempts fail, try without a proxy
        try:
            print("Attempting to connect without a proxy...")
            client = Client()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
            )
            out = response.choices[0].message.content
            if stop:
                stop_indexes = (out.find(s) for s in stop if s in out)
                min_stop = min(stop_indexes, default=-1)
                if min_stop > -1:
                    out = out[:min_stop]
            print("without proxy success")
            return out
        except Exception as e:
            print("Attempting to connect without a proxy...")
            client = Client()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
            )
            out = response.choices[0].message.content
            if stop:
                stop_indexes = (out.find(s) for s in stop if s in out)
                min_stop = min(stop_indexes, default=-1)
                if min_stop > -1:
                    out = out[:min_stop]
            print("without proxy success using gpt-3.5-turbo")
            return out
            # raise Exception(f"Failed to get a response after multiple attempts with proxies and without proxy: {str(e)}")


class JobCategory(str, Enum):
    DATA = "data role"
    BUSINESS = "business role"
    IT = "IT role"

class JobAnalysisOutput(BaseModel):
    skills_in_priority_order: List[str] = Field(description="Top 3 technical tool and tech stack mentioned in job description which is I know as per my resume")
    job_category: JobCategory = Field(description="Categorization of the job role")
    why_this_company: str = Field(description="Personalized 'Why This Company' paragraph")
    why_me: str = Field(description="Personalized 'Why Me' paragraph")
    job_position_title: str = Field(description="Formatted job position title in English")
    company_name: str = Field(description="Formatted company name in English")

def preprocess_job_analysis(result: Tuple[str, Optional[JobAnalysisOutput]]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    job_id, result = result
    new_columns = {
        "job_id": job_id,
        "top_skills": None,
        "job_category": None,
        "why_this_company": None,
        "why_me": None,
    }
    update_columns = {
        "job_id": job_id,
        "job_position_title": None,
        "company_name": None
    }
    
    if result is None:
        return new_columns, update_columns
    
    try:
        skills = result.skills_in_priority_order[:3]
        if "Python" not in skills and "Python" in result.skills_in_priority_order:
            skills = skills[:2] + ["Python"]
        skills_str = ", ".join(skills[:-1]) + ", and " + skills[-1] if len(skills) > 1 else skills[0]
        
        new_columns = {
            "top_skills": skills_str,
            "job_category": result.job_category.value,
            "why_this_company": result.why_this_company,
            "why_me": result.why_me,
        }
        
        update_columns = {
            "job_position_title": result.job_position_title,
            "company_name": result.company_name
        }
        return new_columns, update_columns
    
    except AttributeError as e:
        print(f"AttributeError in preprocess_job_analysis: {e}")
        return new_columns, update_columns

class JobAnalyzer:
    def __init__(self, df: Optional[pd.DataFrame] = None, resume_text: Optional[str] = None):
        self.llm = EducationalLLM()
        self.df = df
        self.resume_text = resume_text
        proxy_rotator.get_proxy()

    def _get_prompt(self) -> PromptTemplate:
        template = """
        Analyze the following job description and resume, then provide the requested information:

        Job Description:
        {job_description}

        Resume:
        {resume}

        Company Name: {company_name}
        
        Job Position Title: {job_position_title}
        

        Please provide the following information:
        1. List the top 3 technical tools and the tech stack that are mentioned in the job description, which I'm familiar with as per my given resume. Include Python by default, listed in priority order.
        2. Categorization of the job role: data role, business role, or IT role
        3. A personalized 'Why This Company' paragraph (see instructions below)
        4. A personalized 'Why Me' paragraph (see instructions below)
        5. A formatted job position title in English, remove any unwanted characters which can't be allowed in directory creation and ensuring it's professional which I can use it in my resume. Make it short if its too long and a typical one.
        6. A formatted company name in English, removing any unwanted characters which can't be allowed in directory or file creation. If the company name is only in French, leave it as is.

        Instructions for 'Why This Company':
        Generate a paragraph that includes the following elements: Do web search and know about company.
        • An understanding of the company's mission, vision, and values.
        • Specific details about the company's products, services, and market position.
        • A mention of the company's reputation and culture.
        • How the company's direction and growth opportunities align with the candidate's career aspirations.
        • Why the candidate is excited about the company.
        example: 'Affirm’s innovative approach to consumer finance is a major factor that draws me to this role. Affirm’s
commitment to transparency and creating consumer-friendly financial products aligns perfectly with my
values and career goals. I am particularly impressed by Affirm’s dedication to eliminating hidden fees and
providing clear, upfront information to consumers, which resonates with my passion for ethical financial
practices. The opportunity to work at a company that leverages cutting-edge technology to optimize
portfolio economics and consumer growth is incredibly exciting to me. I am eager to contribute to Affirm’s
mission of delivering honest financial products that improve lives.'
        length: follow the length of the example provided.

        Instructions for 'Why Me':
        Generate a paragraph that includes the following elements:
        • Relevant experience and skills that match the job requirements.
        • Specific achievements that demonstrate the candidate's capabilities.
        • How the candidate's skills and experience align with the company's needs.
        • The candidate's passion for the industry or role.
        • A brief, professional mention of hoping to master pizza-making before the interview call.
        example: 'With over three years of experience as a Data Analyst, I bring strong analytical skills and proficiency in
SQL, Python, and VBA, essential for the Quantitative Analyst role at Affirm. My achievements include
boosting sales projections by 15% with predictive models and enhancing system reliability through
automated monitoring. My collaborative and problem-solving abilities make me a great fit for this role. I
am confident my technical expertise and passion for fintech innovation will significantly contribute to
Affirm’s success. I look forward to discussing how I can add value, hopefully before perfecting my
homemade pizza recipe!'
        length: follow the length of the example provided.

        Format your response as a JSON object with the following keys:
        skills_in_priority_order, job_category, why_this_company, why_me, job_position_title, company_name
        """
        return PromptTemplate(
            input_variables=["job_description", "resume", "company_name", "job_position_title"],
            template=template
        )
        
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON content from the text and return as a dictionary."""
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                print(f"Failed to parse JSON: {match.group(0)}")
                return {}
        else:
            print(f"No JSON found in the text: {text}")
            return {}

    async def analyze_job(self, job_description, resume, company_name, job_position_title, job_id, attempts=0):
        if attempts >= 3:
            print(f"Failed to analyze job after 3 attempts for {job_position_title} at {company_name}")
            return None

        prompt = self._get_prompt()
        chain = (
            {"job_description": RunnablePassthrough(), "resume": RunnablePassthrough(), "company_name": RunnablePassthrough(), "job_position_title": RunnablePassthrough()}
            | prompt
            | self.llm
            | self._extract_json
        )
        result = await chain.ainvoke({"job_description": job_description, "resume": resume, "company_name": company_name, "job_position_title": job_position_title})
        
        try:
            analysis_output = JobAnalysisOutput(**result)
            return job_id, analysis_output
        except ValueError as e:
            print(f"Validation error (attempt {attempts + 1}): {e}")
            print(f"Raw result: {result}")
            # Recursive call with incremented attempts
            return await self.analyze_job(job_description, resume, company_name, job_position_title, job_id, attempts + 1)


    async def process_jobs(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        if self.df is None or self.resume_text is None:
            raise ValueError("DataFrame and resume text must be provided.")

        tasks = [self.analyze_job(row['job_description'], self.resume_text, row['company_name'], row["job_position_title"], row["job_id"])
            for _, row in self.df.iterrows()]

        results = []
        completed_tasks = 0
        total_tasks = len(tasks)
        print(total_tasks)

        for i in range(0, total_tasks, min(total_tasks, 5)):
            batch = tasks[i:i+min(total_tasks, 5)]
            batch_results = await asyncio.gather(*batch)
            results.extend(batch_results)
            completed_tasks += len(batch)
            print(f"-----------\n Processed {completed_tasks} out of {total_tasks} jobs \n -----------")

        print(f"All tasks completed. Total jobs processed: {completed_tasks}")

        valid_results = [result for result in results if result is not None]

        if not valid_results:
            print("No valid results were obtained.")
            return pd.DataFrame(), pd.DataFrame()

        new_columns, update_columns = zip(*[preprocess_job_analysis(result) for result in valid_results])
        
        df_new = pd.DataFrame(new_columns)
        df_update = pd.DataFrame(update_columns)
        
        # Add job_id to both DataFrames
        df_new['job_id'] = [result[0] for result in valid_results]
        df_update['job_id'] = [result[0] for result in valid_results]
        
        return df_new, df_update



# async def main():
#     def read_pdf_resume(file_path):
#         with open(file_path, 'rb') as file:
#             reader = PyPDF2.PdfReader(file)
#             text = ""
#             for page in reader.pages:
#                 text += page.extract_text()
#         return text
    
#     df = pd.read_csv("job_application_pre_processing.csv")
#     df = df.drop_duplicates(subset='job_id', keep='first')
    
#     # analyzer = JobAnalyzer(df, read_pdf_resume("resume.pdf")) 
#     # df_new, df_update = await analyzer.process_jobs()
    
#     # df_new.to_csv("new_columns.csv", index=False)
#     # df_update.to_csv("update_columns.csv", index=False)
    
#     df_new = pd.read_csv("new_columns.csv")
#     df_update = pd.read_csv("update_columns.csv")
    
#     # Merge new columns
#     df = pd.merge(df, df_new, on='job_id', how='left')
#     # Update existing columns
#     df.update(df_update)
    
#     df.to_csv("test_csv.csv", index=False)

# if __name__ == "__main__":
#     asyncio.run(main())