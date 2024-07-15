from multiprocessing import process
from venv import create
import pandas as pd
from utilities import calculate_posted_time


# Class to process data

data = [
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
]

class ProcessData():
    
    def __init__(self, data):
        self.df_new = self.create_df(data)
        # self.remove_duplicates(self.df_new)
        self.add_posted_date(self.df_new)
    
    def create_df(self, data):
        return pd.DataFrame(data)
    
    def remove_duplicates(self, df):
        df.drop_duplicates(subset=['job_id'], keep='first', inplace=True)
    
    def add_posted_date(self, df):
        df['posted_date'] = df['days_ago'].apply(lambda x: calculate_posted_time(x))

process_data = ProcessData(data)
print(process_data.df_new["posted_date"])