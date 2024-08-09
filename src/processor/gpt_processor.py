import json
import asyncio
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from g4f.client import Client
import pandas as pd
from src.config import GPT_MODEL_PRIMARY, GPT_MODEL_SECONDARY
from src.utilities.proxies import ProxyRotator

# Global proxy rotator
proxy_rotator = ProxyRotator()

success_list = []

class JobCategory(str, Enum):
    DATA_ANALYST = "data analyst role"
    BUSINESS_ANALYST = "business analyst role"
    GENERAL_ANALYST = "general analyst role"
    WEB_DEVELOPER = "web development role"
    NO_MATCH = "no match"

class JobAnalysisOutput(BaseModel):
    skills_in_priority_order: List[str] = Field(description="Top 3 technical tools and tech stack mentioned in job description which I know as per my resume")
    job_category: JobCategory = Field(description="Categorization of the job role")
    why_this_company: str = Field(description="Personalized 'Why This Company' paragraph")
    why_me: str = Field(description="Personalized 'Why Me' paragraph")
    job_position_title: str = Field(description="Formatted job position title in English")
    company_name: str = Field(description="Formatted company name in English")
    location: str = Field(description="Location of company who posted job post")

class EducationalLLM(LLM):
    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(self, prompt: str, stop: Optional[List[str]] = None, run_manager=None,  **kwargs) -> str:
        max_retries = 2
        for attempt in range(max_retries):
            try:
                return self._attempt_call(prompt, stop, **kwargs)
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                proxy_rotator.remove_current_proxy()
        return self._fallback_call(prompt, stop, **kwargs)


    def _attempt_call(self, prompt: str, stop: Optional[List[str]], **kwargs) -> str:
        client = Client(proxies=proxy_rotator.get_proxy())
        response = client.chat.completions.create(
            model=GPT_MODEL_PRIMARY,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        print("success with proxy", response.model, response.provider)
        success_list.append(["success with proxy", response.model,response.provider])
        return self._process_output(response.choices[0].message.content, stop)

    def _fallback_call(self, prompt: str, stop: Optional[List[str]], **kwargs) -> str:
        print("Attempting to connect without a proxy...")
        client = Client()
        response = client.chat.completions.create(
            model=GPT_MODEL_SECONDARY,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        print("success without proxy", response.model, response.provider)
        success_list.append(["success without proxy", response.model, response.provider])
        return self._process_output(response.choices[0].message.content, stop)

    def _process_output(self, output: str, stop: Optional[List[str]]) -> str:
        if stop:
            for s in stop:
                if s in output:
                    output = output[:output.index(s)]
        return output

class JobAnalyzer:
    def __init__(self, df: pd.DataFrame, resume_text: str):
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
        Location: {location}

        Please provide the following information:
        1. List the top 3 technical tools and the tech stack that are mentioned in the job description, which I'm familiar with as per my given resume. Include Python by default if analyst role or else JavaScript if web development role, listed in priority order.
        2. Categorize the job role based on given job description into one of the following categories: data analyst role, business analyst role, general analyst role, web development role, or no match if none apply.
        3. A personalized 'Why This Company' paragraph (see instructions below)
        4. A personalized 'Why Me' paragraph (see instructions below)
        5. A formatted job position title in English only (remove any characters except Alphabets) and give appropriate spacing between words, remove any unwanted characters which can't be allowed in directory creation and ensuring it's professional which I can use it in my resume. Make it short if its too long and a typical one.
        6. A formatted company name in English, removing any unwanted characters which can't be allowed in directory or file creation and give appropriate spacing between words. If the company name is only in French, leave it as is.
        7. Formatted location of company like this "City, Country"
        
        Instructions for 'Why This Company':
        Generate a paragraph that includes the following elements: Do web search and know about company.
        • An understanding of the company's mission, vision, and values.
        • Specific details about the company's products, services, and market position.
        • A mention of the company's reputation and culture.
        • How the company's direction and growth opportunities align with the candidate's career aspirations.
        • Why the candidate is excited about the company.
        example: 'Affirm's innovative approach to consumer finance is a major factor that draws me to this role. Affirm's
        commitment to transparency and creating consumer-friendly financial products aligns perfectly with my
        values and career goals. I am particularly impressed by Affirm's dedication to eliminating hidden fees and
        providing clear, upfront information to consumers, which resonates with my passion for ethical financial
        practices. The opportunity to work at a company that leverages cutting-edge technology to optimize
        portfolio economics and consumer growth is incredibly exciting to me. I am eager to contribute to Affirm's
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
        Affirm's success. I look forward to discussing how I can add value, hopefully before perfecting my
        homemade pizza recipe!'
        length: follow the length of the example provided.


        Format your response as a JSON object with the following keys:
        skills_in_priority_order, job_category, why_this_company, why_me, job_position_title, company_name, location.
        """
        return PromptTemplate(
            input_variables=["job_description", "resume", "company_name", "job_position_title", "location"],
            template=template
        )

    def _extract_json(self, text: str) -> Dict[str, Any]:
        try:
            if text[:7] == "```json":
                text = text[7:]
                text=text[:-3]
            return json.loads(text)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {text}")
            return {}

    async def analyze_job(self, job_description: str, resume: str, company_name: str, job_position_title: str, job_id: str, location: str) -> Optional[Tuple[str, JobAnalysisOutput]]:
        prompt = self._get_prompt()
        chain = (
            {"job_description": RunnablePassthrough(), "resume": RunnablePassthrough(), "company_name": RunnablePassthrough(), "job_position_title": RunnablePassthrough(), "location": RunnablePassthrough()}
            | prompt
            | self.llm
            | self._extract_json
        )
        result = await chain.ainvoke({"job_description": job_description, "resume": resume, "company_name": company_name, "job_position_title": job_position_title, "location": location})
        
        try:
            analysis_output = JobAnalysisOutput(**result)
            return job_id, analysis_output
        except ValueError as e:
            print(f"Validation error: {e}")
            print(f"Raw result: {result}")
            return None

    async def process_jobs(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        if self.df is None or self.resume_text is None:
            raise ValueError("DataFrame and resume text must be provided.")

        tasks = [self.analyze_job(row['job_description'], self.resume_text, row['company_name'], row["job_position_title"], row["job_id"], row["location"])
            for _, row in self.df.iterrows()]

        results = []
        completed_tasks = 0
        total_tasks = len(tasks)
        print(f"Total jobs to process: {total_tasks}")

        for i in range(0, total_tasks, 5):
            batch = tasks[i:i+5]
            batch_results = await asyncio.gather(*batch)
            results.extend(batch_results)
            completed_tasks += len(batch)
            print(f"Processed {completed_tasks} out of {total_tasks} jobs")

        print(f"All tasks completed. Total jobs processed: {completed_tasks}")

        valid_results = [result for result in results if result is not None]

        if not valid_results:
            print("No valid results were obtained.")
            return pd.DataFrame(), pd.DataFrame()

        new_columns, update_columns = zip(*[self._preprocess_job_analysis(result) for result in valid_results])
        
        df_new = pd.DataFrame(new_columns)
        df_update = pd.DataFrame(update_columns)
        
        df_new['job_id'] = [result[0] for result in valid_results]
        df_update['job_id'] = [result[0] for result in valid_results]
        
        return df_new, df_update


    @staticmethod
    def _preprocess_job_analysis(result: Tuple[str, JobAnalysisOutput]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        job_id, output = result
        new_columns = {
            "job_id": job_id,
            "top_skills": ", ".join(output.skills_in_priority_order),
            "job_category": output.job_category,
            "why_this_company": output.why_this_company,
            "why_me": output.why_me,
        }
        update_columns = {
            "job_id": job_id,
            "job_position_title": output.job_position_title,
            "company_name": output.company_name,
            "location": output.location
        }
        return new_columns, update_columns

if __name__ == "__main__":
    # Initialize the proxy rotator
    
    
    # Add any test or example usage here
    pass
