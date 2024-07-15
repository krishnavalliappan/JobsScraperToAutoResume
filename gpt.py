import json
import asyncio
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
import g4f
import PyPDF2
import re

class EducationalLLM(LLM):
    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(self, prompt: str, stop: Optional[List[str]] = None, run_manager=None, **kwargs) -> str:
        out = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4o,
            messages=[{"role": "user", "content": prompt}],
        )
        if stop:
            stop_indexes = (out.find(s) for s in stop if s in out)
            min_stop = min(stop_indexes, default=-1)
            if min_stop > -1:
                out = out[:min_stop]
        return out

class JobCategory(str, Enum):
    DATA = "data role"
    BUSINESS = "business role"
    IT = "IT infrastructure role"

class JobAnalysisOutput(BaseModel):
    skills_in_priority_order: List[str] = Field(description="Top 3 technical tool and tech stack mentioned in job description")
    job_category: JobCategory = Field(description="Categorization of the job role")
    why_this_company: str = Field(description="Personalized 'Why This Company' paragraph")
    why_me: str = Field(description="Personalized 'Why Me' paragraph")

def read_pdf_resume(file_path: str) -> str:
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

class JobAnalyzer:
    def __init__(self):
        self.llm = EducationalLLM()

    def _get_prompt(self):
        template = """
        Analyze the following job description and resume, then provide the requested information:

        Job Description:
        {job_description}

        Resume:
        {resume}

        Company Name: {company_name}

        Please provide the following information:
        1. Top 3 technical tools and tech stack mentioned in the job description. List them in priority order. Inlcude Python by default.
        2. Categorization of the job role: data role, business role, or IT infrastructure role
        3. A personalized 'Why This Company' paragraph (see instructions below)
        4. A personalized 'Why Me' paragraph (see instructions below)

        Instructions for 'Why This Company':
        Generate a paragraph that includes the following elements: Do web search and know about company.
        • An understanding of the company's mission, vision, and values.
        • Specific details about the company's products, services, and market position.
        • A mention of the company's reputation and culture.
        • How the company's direction and growth opportunities align with the candidate's career aspirations.
        • Why the candidate is excited about the company.
        example for company name "Affirm": Affirm’s innovative approach to consumer finance is a major factor that draws me to this role. Affirm’s commitment to transparency and creating consumer-friendly financial products aligns perfectly with my values and career goals. I am particularly impressed by Affirm’s dedication to eliminating hidden fees and providing clear, upfront information to consumers, which resonates with my passion for ethical financial practices. The opportunity to work at a company that leverages cutting-edge technology to optimize portfolio economics and consumer growth is incredibly exciting to me. I am eager to contribute to Affirm’s mission of delivering honest financial products that improve lives.

        Instructions for 'Why Me':
        Generate a paragraph that includes the following elements:
        • Relevant experience and skills that match the job requirements.
        • Specific achievements that demonstrate the candidate's capabilities.
        • How the candidate's skills and experience align with the company's needs.
        • The candidate's passion for the industry or role.
        • A brief, professional mention of hoping to master pizza-making before the interview call.
        example for company name "Affirm": With over three years of experience as a Data Analyst, I bring strong analytical skills and proficiency in SQL, Python, and VBA, essential for the Quantitative Analyst role at Affirm. My achievements include boosting sales projections by 15% with predictive models and enhancing system reliability through automated monitoring. My collaborative and problem-solving abilities make me a great fit for this role. I am confident my technical expertise and passion for fintech innovation will significantly contribute to Affirm’s success. I look forward to discussing how I can add value, hopefully before perfecting my homemade pizza recipe!” 

        Format your response as a JSON object with the following keys:
        skills_in_priority_order, job_category, why_this_company, why_me
        """
        return PromptTemplate(
            input_variables=["job_description", "resume", "company_name"],
            template=template
        )
        
    def _extract_json(self, text: str) -> str:
        """Extract JSON content from the text."""
        match = re.search(r'\{[\s\S]*\}', text)
        return match.group(0) if match else '{}'

    async def analyze_job(self, job_description, resume, company_name):
        prompt = self._get_prompt()
        chain = (
            {"job_description": RunnablePassthrough(), "resume": RunnablePassthrough(), "company_name": RunnablePassthrough()}
            | prompt
            | self.llm
            | self._extract_json
            | (lambda x: json.loads(x))
            | JobAnalysisOutput.model_validate
        )
        return await chain.ainvoke({"job_description": job_description, "resume": resume, "company_name": company_name})

def preprocess_job_analysis(result: JobAnalysisOutput, company_name: str):
    skills = result.skills_in_priority_order[:3]
    if "Python" not in skills and "Python" in result.skills_in_priority_order:
        skills = skills[:2] + ["Python"]
    
    formatted_output = {
        "Skills": skills,
        "Job Category": result.job_category.value,
        f"Why This {company_name}": result.why_this_company,
        "Why Me":result.why_me
    }
    return formatted_output

# Usage example
async def process_job(data, resume_text, analyzer):
    job_description = data['job_description']
    company_name = data['company_name']
    result = await analyzer.analyze_job(job_description, resume_text, company_name)
    return preprocess_job_analysis(result, company_name)

async def main():
    analyzer = JobAnalyzer()
    resume_text = read_pdf_resume("resume.pdf")
    
    datas = [
{'job_position_title': 'Data Analyst', 
'job_id': '3974374856', 
'job_position_link': 'https://www.linkedin.com/jobs/view/3974374856/?alternateChannel=search&refId=yhj%2BI8Ew%2F%2B6040dGv3bByw%3D%3D&trackingId=p8oC8tmOzeHlEncsgw7D1Q%3D%3D&trk=d_flagship3_search_srp_jobs', 
'company_logo': 'https://media.licdn.com/dms/image/D560BAQE2MFxEo3KTBg/company-logo_100_100/0/1719871928173/actalentservices_logo?e=1729123200&v=beta&t=eXWO4kauMPFV6URI_6YIUlSkB8oMIy7Kt4Fi8fe4MmU', 
'company_name': 'Actalent', 
'location': 'North Vancouver, BC', 
'days_ago': 'hours ago', 
'no_of_applicants': 0, 
'salary': None,
'workplace': 'On-site', 
'job_type': 'Contract', 
'experience_level': 'Entry level', 
'industry': 'Business Consulting and Services', 
'is_easy_apply': False, 
'apply_link': 'https://careers.actalentservices.com/us/en/job/JP-004574111/Data-Analyst?utm_source=Recruitics&utm_medium=equest&s_id=4106&icid=linkedin_limited_listings_recruitics&id=2153&rx_job=JP-004574111&rx_medium=post&rx_paid=0&rx_r=none&rx_source=LinkedIn&rx_ts=20240712T145001Z&rx_viewer=c3aad9af408011efb9a3e703f419abee4b16510d6bb74803815eb41d3e0278e7', 
'job_description': "About the job Job Title: Data Analyst  Job Description  As a Data Analyst, you will be integral in developing and implementing quality control plans for projects to ensure they meet established standards and customer requirements. Your role will involve optimizing processes, collaborating with cross-functional teams, and using data analytics to enhance project performance. You will be responsible for developing tools, maintaining a centralized data repository, and using statistical analysis to identify and address quality issues. Additionally, you will develop training materials, provide training, and communicate insights and recommendations directly to customers.  Hard Skills  Power BI Excel Data Visualization Statistical Analysis Quality Control Industrial or Manufacturing Experience  Soft Skills  Process Improvement Cross-functional Collaboration Communication Proactive Metrics Development Training & Development  Work Site  Vancouver  À propos d'Actalent:  Actalent est un chef de file mondial des services d’ingénierie et de sciences et des solutions de talents. Nous aidons les entreprises visionnaires à faire progresser leurs initiatives en matière d’ingénierie et de science en leur donnant accès à des experts spécialisés qui favorisent la mise à l’échelle, l’innovation et la mise en marché rapide. Avec un réseau de près de 30\u202f000\u202fconsultants et plus de 4\u202f500\u202fclients aux États-Unis, au Canada, en Asie et en Europe, Actalent est au service d’un grand nombre d’entreprises du classement Fortune 500.  La diversité, l’équité et l’inclusion  Chez Actalent, la diversité et l’inclusion constituent le pont vers l’équité et la réussite de notre personnel. La diversité, l’équité et l’inclusion (DE&I) sont ancrées dans notre culture par\u202f:  L’embauche des talents diversifiés ; Le maintien d’un environnement inclusif par une autoréflexion permanente ; La mise en place d’une culture de soin, d’engagement, et de reconnaissance par des résultats concrets ; L’assurance des opportunités de croissance pour nos gens.  Actalent est un employeur souscrivant au principe de l’égalité des chances et accepte toutes les candidatures sans tenir compte de la race, du sexe, de l’âge, de la couleur, de la religion, des origines nationales, du statut d’ancien combattant, d’un handicap, de l’orientation sexuelle, de l’identité sexuelle, des renseignements génétiques ou de toute autre caractéristique protégée par la loi.  Si vous souhaitez faire une demande d’accommodement raisonnable, tel que la modification ou l’ajustement du processus de demande d’emploi ou d’entrevue à cause d’un handicap, veuillez envoyer un courriel à actalentaccommodation@actalentservices.com pour connaître d’autres options d’accommodement.  About Actalent  Actalent is a global leader in engineering and sciences services and talent solutions. We help visionary companies advance their engineering and science initiatives through access to specialized experts who drive scale, innovation and speed to market. With a network of almost 30,000 consultants and more than 4,500 clients across the U.S., Canada, Asia and Europe, Actalent serves many of the Fortune 500.  Diversity, Equity & Inclusion  At Actalent, diversity and inclusion are a bridge towards the equity and success of our people. DE&I are embedded into our culture through:  Hiring diverse talent Maintaining an inclusive environment through persistent self-reflection Building a culture of care, engagement, and recognition with clear outcomes Ensuring growth opportunities for our people  The company is an equal opportunity employer and will consider all applications without regard to race, sex, age, color, religion, national origin, veteran status, disability, sexual orientation, gender identity, genetic information or any characteristic protected by law.  If you would like to request a reasonable accommodation, such as the modification or adjustment of the job application process or interviewing process due to a disability, please email actalentaccommodation@actalentservices.com for other accommodation options."}
,{'job_position_title': 'Data Analyst', 
'job_id': '3974374856', 
'job_position_link': 'https://www.linkedin.com/jobs/view/3974374856/?alternateChannel=search&refId=yhj%2BI8Ew%2F%2B6040dGv3bByw%3D%3D&trackingId=p8oC8tmOzeHlEncsgw7D1Q%3D%3D&trk=d_flagship3_search_srp_jobs', 
'company_logo': 'https://media.licdn.com/dms/image/D560BAQE2MFxEo3KTBg/company-logo_100_100/0/1719871928173/actalentservices_logo?e=1729123200&v=beta&t=eXWO4kauMPFV6URI_6YIUlSkB8oMIy7Kt4Fi8fe4MmU', 
'company_name': 'Actalent', 
'location': 'North Vancouver, BC', 
'days_ago': '2 hours ago', 
'no_of_applicants': 0, 
'salary': None,
'workplace': 'On-site', 
'job_type': 'Contract', 
'experience_level': 'Entry level', 
'industry': 'Business Consulting and Services', 
'is_easy_apply': False, 
'apply_link': 'https://careers.actalentservices.com/us/en/job/JP-004574111/Data-Analyst?utm_source=Recruitics&utm_medium=equest&s_id=4106&icid=linkedin_limited_listings_recruitics&id=2153&rx_job=JP-004574111&rx_medium=post&rx_paid=0&rx_r=none&rx_source=LinkedIn&rx_ts=20240712T145001Z&rx_viewer=c3aad9af408011efb9a3e703f419abee4b16510d6bb74803815eb41d3e0278e7', 
'job_description': "About the job Job Title: Data Analyst  Job Description  As a Data Analyst, you will be integral in developing and implementing quality control plans for projects to ensure they meet established standards and customer requirements. Your role will involve optimizing processes, collaborating with cross-functional teams, and using data analytics to enhance project performance. You will be responsible for developing tools, maintaining a centralized data repository, and using statistical analysis to identify and address quality issues. Additionally, you will develop training materials, provide training, and communicate insights and recommendations directly to customers.  Hard Skills  Power BI Excel Data Visualization Statistical Analysis Quality Control Industrial or Manufacturing Experience  Soft Skills  Process Improvement Cross-functional Collaboration Communication Proactive Metrics Development Training & Development  Work Site  Vancouver  À propos d'Actalent:  Actalent est un chef de file mondial des services d’ingénierie et de sciences et des solutions de talents. Nous aidons les entreprises visionnaires à faire progresser leurs initiatives en matière d’ingénierie et de science en leur donnant accès à des experts spécialisés qui favorisent la mise à l’échelle, l’innovation et la mise en marché rapide. Avec un réseau de près de 30\u202f000\u202fconsultants et plus de 4\u202f500\u202fclients aux États-Unis, au Canada, en Asie et en Europe, Actalent est au service d’un grand nombre d’entreprises du classement Fortune 500.  La diversité, l’équité et l’inclusion  Chez Actalent, la diversité et l’inclusion constituent le pont vers l’équité et la réussite de notre personnel. La diversité, l’équité et l’inclusion (DE&I) sont ancrées dans notre culture par\u202f:  L’embauche des talents diversifiés ; Le maintien d’un environnement inclusif par une autoréflexion permanente ; La mise en place d’une culture de soin, d’engagement, et de reconnaissance par des résultats concrets ; L’assurance des opportunités de croissance pour nos gens.  Actalent est un employeur souscrivant au principe de l’égalité des chances et accepte toutes les candidatures sans tenir compte de la race, du sexe, de l’âge, de la couleur, de la religion, des origines nationales, du statut d’ancien combattant, d’un handicap, de l’orientation sexuelle, de l’identité sexuelle, des renseignements génétiques ou de toute autre caractéristique protégée par la loi.  Si vous souhaitez faire une demande d’accommodement raisonnable, tel que la modification ou l’ajustement du processus de demande d’emploi ou d’entrevue à cause d’un handicap, veuillez envoyer un courriel à actalentaccommodation@actalentservices.com pour connaître d’autres options d’accommodement.  About Actalent  Actalent is a global leader in engineering and sciences services and talent solutions. We help visionary companies advance their engineering and science initiatives through access to specialized experts who drive scale, innovation and speed to market. With a network of almost 30,000 consultants and more than 4,500 clients across the U.S., Canada, Asia and Europe, Actalent serves many of the Fortune 500.  Diversity, Equity & Inclusion  At Actalent, diversity and inclusion are a bridge towards the equity and success of our people. DE&I are embedded into our culture through:  Hiring diverse talent Maintaining an inclusive environment through persistent self-reflection Building a culture of care, engagement, and recognition with clear outcomes Ensuring growth opportunities for our people  The company is an equal opportunity employer and will consider all applications without regard to race, sex, age, color, religion, national origin, veteran status, disability, sexual orientation, gender identity, genetic information or any characteristic protected by law.  If you would like to request a reasonable accommodation, such as the modification or adjustment of the job application process or interviewing process due to a disability, please email actalentaccommodation@actalentservices.com for other accommodation options."}
,{'job_position_title': 'Data Analyst', 
'job_id': '3974374856', 
'job_position_link': 'https://www.linkedin.com/jobs/view/3974374856/?alternateChannel=search&refId=yhj%2BI8Ew%2F%2B6040dGv3bByw%3D%3D&trackingId=p8oC8tmOzeHlEncsgw7D1Q%3D%3D&trk=d_flagship3_search_srp_jobs', 
'company_logo': 'https://media.licdn.com/dms/image/D560BAQE2MFxEo3KTBg/company-logo_100_100/0/1719871928173/actalentservices_logo?e=1729123200&v=beta&t=eXWO4kauMPFV6URI_6YIUlSkB8oMIy7Kt4Fi8fe4MmU', 
'company_name': 'Actalent', 
'location': 'North Vancouver, BC', 
'days_ago': 'hours ago', 
'no_of_applicants': 0, 
'salary': None,
'workplace': 'On-site', 
'job_type': 'Contract', 
'experience_level': 'Entry level', 
'industry': 'Business Consulting and Services', 
'is_easy_apply': False, 
'apply_link': 'https://careers.actalentservices.com/us/en/job/JP-004574111/Data-Analyst?utm_source=Recruitics&utm_medium=equest&s_id=4106&icid=linkedin_limited_listings_recruitics&id=2153&rx_job=JP-004574111&rx_medium=post&rx_paid=0&rx_r=none&rx_source=LinkedIn&rx_ts=20240712T145001Z&rx_viewer=c3aad9af408011efb9a3e703f419abee4b16510d6bb74803815eb41d3e0278e7', 
'job_description': "About the job Job Title: Data Analyst  Job Description  As a Data Analyst, you will be integral in developing and implementing quality control plans for projects to ensure they meet established standards and customer requirements. Your role will involve optimizing processes, collaborating with cross-functional teams, and using data analytics to enhance project performance. You will be responsible for developing tools, maintaining a centralized data repository, and using statistical analysis to identify and address quality issues. Additionally, you will develop training materials, provide training, and communicate insights and recommendations directly to customers.  Hard Skills  Power BI Excel Data Visualization Statistical Analysis Quality Control Industrial or Manufacturing Experience  Soft Skills  Process Improvement Cross-functional Collaboration Communication Proactive Metrics Development Training & Development  Work Site  Vancouver  À propos d'Actalent:  Actalent est un chef de file mondial des services d’ingénierie et de sciences et des solutions de talents. Nous aidons les entreprises visionnaires à faire progresser leurs initiatives en matière d’ingénierie et de science en leur donnant accès à des experts spécialisés qui favorisent la mise à l’échelle, l’innovation et la mise en marché rapide. Avec un réseau de près de 30\u202f000\u202fconsultants et plus de 4\u202f500\u202fclients aux États-Unis, au Canada, en Asie et en Europe, Actalent est au service d’un grand nombre d’entreprises du classement Fortune 500.  La diversité, l’équité et l’inclusion  Chez Actalent, la diversité et l’inclusion constituent le pont vers l’équité et la réussite de notre personnel. La diversité, l’équité et l’inclusion (DE&I) sont ancrées dans notre culture par\u202f:  L’embauche des talents diversifiés ; Le maintien d’un environnement inclusif par une autoréflexion permanente ; La mise en place d’une culture de soin, d’engagement, et de reconnaissance par des résultats concrets ; L’assurance des opportunités de croissance pour nos gens.  Actalent est un employeur souscrivant au principe de l’égalité des chances et accepte toutes les candidatures sans tenir compte de la race, du sexe, de l’âge, de la couleur, de la religion, des origines nationales, du statut d’ancien combattant, d’un handicap, de l’orientation sexuelle, de l’identité sexuelle, des renseignements génétiques ou de toute autre caractéristique protégée par la loi.  Si vous souhaitez faire une demande d’accommodement raisonnable, tel que la modification ou l’ajustement du processus de demande d’emploi ou d’entrevue à cause d’un handicap, veuillez envoyer un courriel à actalentaccommodation@actalentservices.com pour connaître d’autres options d’accommodement.  About Actalent  Actalent is a global leader in engineering and sciences services and talent solutions. We help visionary companies advance their engineering and science initiatives through access to specialized experts who drive scale, innovation and speed to market. With a network of almost 30,000 consultants and more than 4,500 clients across the U.S., Canada, Asia and Europe, Actalent serves many of the Fortune 500.  Diversity, Equity & Inclusion  At Actalent, diversity and inclusion are a bridge towards the equity and success of our people. DE&I are embedded into our culture through:  Hiring diverse talent Maintaining an inclusive environment through persistent self-reflection Building a culture of care, engagement, and recognition with clear outcomes Ensuring growth opportunities for our people  The company is an equal opportunity employer and will consider all applications without regard to race, sex, age, color, religion, national origin, veteran status, disability, sexual orientation, gender identity, genetic information or any characteristic protected by law.  If you would like to request a reasonable accommodation, such as the modification or adjustment of the job application process or interviewing process due to a disability, please email actalentaccommodation@actalentservices.com for other accommodation options."}
,{'job_position_title': 'Data Analyst', 
'job_id': '3974374856', 
'job_position_link': 'https://www.linkedin.com/jobs/view/3974374856/?alternateChannel=search&refId=yhj%2BI8Ew%2F%2B6040dGv3bByw%3D%3D&trackingId=p8oC8tmOzeHlEncsgw7D1Q%3D%3D&trk=d_flagship3_search_srp_jobs', 
'company_logo': 'https://media.licdn.com/dms/image/D560BAQE2MFxEo3KTBg/company-logo_100_100/0/1719871928173/actalentservices_logo?e=1729123200&v=beta&t=eXWO4kauMPFV6URI_6YIUlSkB8oMIy7Kt4Fi8fe4MmU', 
'company_name': 'Actalent', 
'location': 'North Vancouver, BC', 
'days_ago': 'hours ago', 
'no_of_applicants': 0, 
'salary': None,
'workplace': 'On-site', 
'job_type': 'Contract', 
'experience_level': 'Entry level', 
'industry': 'Business Consulting and Services', 
'is_easy_apply': False, 
'apply_link': 'https://careers.actalentservices.com/us/en/job/JP-004574111/Data-Analyst?utm_source=Recruitics&utm_medium=equest&s_id=4106&icid=linkedin_limited_listings_recruitics&id=2153&rx_job=JP-004574111&rx_medium=post&rx_paid=0&rx_r=none&rx_source=LinkedIn&rx_ts=20240712T145001Z&rx_viewer=c3aad9af408011efb9a3e703f419abee4b16510d6bb74803815eb41d3e0278e7', 
'job_description': "About the job Job Title: Data Analyst  Job Description  As a Data Analyst, you will be integral in developing and implementing quality control plans for projects to ensure they meet established standards and customer requirements. Your role will involve optimizing processes, collaborating with cross-functional teams, and using data analytics to enhance project performance. You will be responsible for developing tools, maintaining a centralized data repository, and using statistical analysis to identify and address quality issues. Additionally, you will develop training materials, provide training, and communicate insights and recommendations directly to customers.  Hard Skills  Power BI Excel Data Visualization Statistical Analysis Quality Control Industrial or Manufacturing Experience  Soft Skills  Process Improvement Cross-functional Collaboration Communication Proactive Metrics Development Training & Development  Work Site  Vancouver  À propos d'Actalent:  Actalent est un chef de file mondial des services d’ingénierie et de sciences et des solutions de talents. Nous aidons les entreprises visionnaires à faire progresser leurs initiatives en matière d’ingénierie et de science en leur donnant accès à des experts spécialisés qui favorisent la mise à l’échelle, l’innovation et la mise en marché rapide. Avec un réseau de près de 30\u202f000\u202fconsultants et plus de 4\u202f500\u202fclients aux États-Unis, au Canada, en Asie et en Europe, Actalent est au service d’un grand nombre d’entreprises du classement Fortune 500.  La diversité, l’équité et l’inclusion  Chez Actalent, la diversité et l’inclusion constituent le pont vers l’équité et la réussite de notre personnel. La diversité, l’équité et l’inclusion (DE&I) sont ancrées dans notre culture par\u202f:  L’embauche des talents diversifiés ; Le maintien d’un environnement inclusif par une autoréflexion permanente ; La mise en place d’une culture de soin, d’engagement, et de reconnaissance par des résultats concrets ; L’assurance des opportunités de croissance pour nos gens.  Actalent est un employeur souscrivant au principe de l’égalité des chances et accepte toutes les candidatures sans tenir compte de la race, du sexe, de l’âge, de la couleur, de la religion, des origines nationales, du statut d’ancien combattant, d’un handicap, de l’orientation sexuelle, de l’identité sexuelle, des renseignements génétiques ou de toute autre caractéristique protégée par la loi.  Si vous souhaitez faire une demande d’accommodement raisonnable, tel que la modification ou l’ajustement du processus de demande d’emploi ou d’entrevue à cause d’un handicap, veuillez envoyer un courriel à actalentaccommodation@actalentservices.com pour connaître d’autres options d’accommodement.  About Actalent  Actalent is a global leader in engineering and sciences services and talent solutions. We help visionary companies advance their engineering and science initiatives through access to specialized experts who drive scale, innovation and speed to market. With a network of almost 30,000 consultants and more than 4,500 clients across the U.S., Canada, Asia and Europe, Actalent serves many of the Fortune 500.  Diversity, Equity & Inclusion  At Actalent, diversity and inclusion are a bridge towards the equity and success of our people. DE&I are embedded into our culture through:  Hiring diverse talent Maintaining an inclusive environment through persistent self-reflection Building a culture of care, engagement, and recognition with clear outcomes Ensuring growth opportunities for our people  The company is an equal opportunity employer and will consider all applications without regard to race, sex, age, color, religion, national origin, veteran status, disability, sexual orientation, gender identity, genetic information or any characteristic protected by law.  If you would like to request a reasonable accommodation, such as the modification or adjustment of the job application process or interviewing process due to a disability, please email actalentaccommodation@actalentservices.com for other accommodation options."}
,{'job_position_title': 'Data Analyst', 
'job_id': '3974374856', 
'job_position_link': 'https://www.linkedin.com/jobs/view/3974374856/?alternateChannel=search&refId=yhj%2BI8Ew%2F%2B6040dGv3bByw%3D%3D&trackingId=p8oC8tmOzeHlEncsgw7D1Q%3D%3D&trk=d_flagship3_search_srp_jobs', 
'company_logo': 'https://media.licdn.com/dms/image/D560BAQE2MFxEo3KTBg/company-logo_100_100/0/1719871928173/actalentservices_logo?e=1729123200&v=beta&t=eXWO4kauMPFV6URI_6YIUlSkB8oMIy7Kt4Fi8fe4MmU', 
'company_name': 'Actalent', 
'location': 'North Vancouver, BC', 
'days_ago': 'hours ago', 
'no_of_applicants': 0, 
'salary': None,
'workplace': 'On-site', 
'job_type': 'Contract', 
'experience_level': 'Entry level', 
'industry': 'Business Consulting and Services', 
'is_easy_apply': False, 
'apply_link': 'https://careers.actalentservices.com/us/en/job/JP-004574111/Data-Analyst?utm_source=Recruitics&utm_medium=equest&s_id=4106&icid=linkedin_limited_listings_recruitics&id=2153&rx_job=JP-004574111&rx_medium=post&rx_paid=0&rx_r=none&rx_source=LinkedIn&rx_ts=20240712T145001Z&rx_viewer=c3aad9af408011efb9a3e703f419abee4b16510d6bb74803815eb41d3e0278e7', 
'job_description': "About the job Job Title: Data Analyst  Job Description  As a Data Analyst, you will be integral in developing and implementing quality control plans for projects to ensure they meet established standards and customer requirements. Your role will involve optimizing processes, collaborating with cross-functional teams, and using data analytics to enhance project performance. You will be responsible for developing tools, maintaining a centralized data repository, and using statistical analysis to identify and address quality issues. Additionally, you will develop training materials, provide training, and communicate insights and recommendations directly to customers.  Hard Skills  Power BI Excel Data Visualization Statistical Analysis Quality Control Industrial or Manufacturing Experience  Soft Skills  Process Improvement Cross-functional Collaboration Communication Proactive Metrics Development Training & Development  Work Site  Vancouver  À propos d'Actalent:  Actalent est un chef de file mondial des services d’ingénierie et de sciences et des solutions de talents. Nous aidons les entreprises visionnaires à faire progresser leurs initiatives en matière d’ingénierie et de science en leur donnant accès à des experts spécialisés qui favorisent la mise à l’échelle, l’innovation et la mise en marché rapide. Avec un réseau de près de 30\u202f000\u202fconsultants et plus de 4\u202f500\u202fclients aux États-Unis, au Canada, en Asie et en Europe, Actalent est au service d’un grand nombre d’entreprises du classement Fortune 500.  La diversité, l’équité et l’inclusion  Chez Actalent, la diversité et l’inclusion constituent le pont vers l’équité et la réussite de notre personnel. La diversité, l’équité et l’inclusion (DE&I) sont ancrées dans notre culture par\u202f:  L’embauche des talents diversifiés ; Le maintien d’un environnement inclusif par une autoréflexion permanente ; La mise en place d’une culture de soin, d’engagement, et de reconnaissance par des résultats concrets ; L’assurance des opportunités de croissance pour nos gens.  Actalent est un employeur souscrivant au principe de l’égalité des chances et accepte toutes les candidatures sans tenir compte de la race, du sexe, de l’âge, de la couleur, de la religion, des origines nationales, du statut d’ancien combattant, d’un handicap, de l’orientation sexuelle, de l’identité sexuelle, des renseignements génétiques ou de toute autre caractéristique protégée par la loi.  Si vous souhaitez faire une demande d’accommodement raisonnable, tel que la modification ou l’ajustement du processus de demande d’emploi ou d’entrevue à cause d’un handicap, veuillez envoyer un courriel à actalentaccommodation@actalentservices.com pour connaître d’autres options d’accommodement.  About Actalent  Actalent is a global leader in engineering and sciences services and talent solutions. We help visionary companies advance their engineering and science initiatives through access to specialized experts who drive scale, innovation and speed to market. With a network of almost 30,000 consultants and more than 4,500 clients across the U.S., Canada, Asia and Europe, Actalent serves many of the Fortune 500.  Diversity, Equity & Inclusion  At Actalent, diversity and inclusion are a bridge towards the equity and success of our people. DE&I are embedded into our culture through:  Hiring diverse talent Maintaining an inclusive environment through persistent self-reflection Building a culture of care, engagement, and recognition with clear outcomes Ensuring growth opportunities for our people  The company is an equal opportunity employer and will consider all applications without regard to race, sex, age, color, religion, national origin, veteran status, disability, sexual orientation, gender identity, genetic information or any characteristic protected by law.  If you would like to request a reasonable accommodation, such as the modification or adjustment of the job application process or interviewing process due to a disability, please email actalentaccommodation@actalentservices.com for other accommodation options."}
,]

    tasks = [process_job(data, resume_text, analyzer) for data in datas]
    results = await asyncio.gather(*tasks)

    for result in results:
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
