import requests
from bs4 import BeautifulSoup
import pandas as pd
import os 
from datetime import datetime
import re
import logging
import sentry_sdk
from sentry_sdk import capture_message
from sentry_sdk.integrations.logging import LoggingIntegration
from dotenv import load_dotenv


load_dotenv()

sentry_logging = LoggingIntegration(
    level=logging.DEBUG,       
    event_level=logging.DEBUG  
)
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[
        sentry_logging,
    ],
    traces_sample_rate=1.0,
)

def get_foreign_hearings(rows: int):

    url = "https://www.foreign.senate.gov/hearings?maxrows=" + str(rows)
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'https://github.com/Leschonander/SenateVideoScraper'  
    }
    res = requests.get(url, headers=headers)

    soup =  BeautifulSoup(res.text,'html.parser')

    table_rows = soup.findAll('a', { 'class': 'LegislationList__item'})
    data = []
    for t in table_rows:
        if t.find('time') == None:
            date = ""
            time = ""
        else:
            date_time = t.find('time').get_text().replace("\n", "").replace("\t", "").strip().split("at")
            
        try:
            date = date_time[0].strip()
        except:
            date = ""
        try:
            time = date_time[2].strip()
        except IndexError:
            time = ""
        
        try:
            title = t.find("div", {'class': "LegislationList__title LegislationList__itemText"}).get_text().replace("\n", "").replace("\t", "").strip()
        except:
            title = ""
        

        url = t["href"]

        if  t.find("div", {'class': "LegislationList__itemText"}) == None:
            location = ""
        else:
            location =  t.findAll("div", {'class': "LegislationList__itemText"})[2].get_text().rstrip().lstrip()
        
            
        row_obj = {
            "Date": date,
            "Time": time,
            "URL": url,
            "Title": title,
            "Location": location,
            "Committee": "Foreign",
            "Date Scraped": datetime.today().strftime("%Y-%m-%d")
        }
        
        data.append(row_obj)
    
    for d in data:
        if d["URL"] == "":
            d["video_url"] = ""
        else:
            res_ind = requests.get(d["URL"], headers=headers)
            soup_ind = BeautifulSoup(res_ind.text,'html.parser')
            
            if soup_ind.find('iframe', { 'class': 'streaminghearing'}) == None:
                video_url = ""
            else:
                video_url =  soup_ind.find('iframe', { 'class': 'streaminghearing'})["src"]
            
            d["video_url"] = video_url

            if soup_ind.findAll('li', {'class': 'col-12'}) == None:
                d["witnesses"] = ""
                d["transcripts"] = ""
                d["witness_transcripts"] = ""
                if "Closed" in d["Title"] or "RESCHEDULED" in d["Title"] or "POSTPONED" in d["Title"]  or time.strptime(d["Date"], '%m/%d/%y') > datetime.today():
                    logging.error(f'{d["Title"]} at {d["Date"]} lacks witness and transcript information.')

            else:
                witness_cards = soup_ind.findAll("li", {"class": "col-12"})
                witness = []
                transcripts = []
                witness_transcripts = []

                for w in witness_cards:
                    
                    witness_name = w.find('span',  {'class': 'bold'}).get_text().replace("\t", "").replace("\n", " ").replace("0x80", "").strip()
                    witness_name = witness_name.replace("Hon.", "").replace("Mr.", "").replace("Ms.", "").replace("Mrs.", "").replace("Dr.", "").replace("Ph.D.", "").replace("PhD", "").replace("Senator", "").replace("Representative", "").replace("Lt", "").replace("The Honorable", "").replace("(R-GA)", "").strip() 
                    witness_name = ' '.join(witness_name.split())

                    if w.find('div',  {'class': 'mt-3'}) == None:
                        witness_url = ''
                        if "Closed" in d["Title"] or "RESCHEDULED" in d["Title"] or "POSTPONED" in d["Title"]:
                            logging.error(f'{d["Title"]} at {d["Date"]} lacks witness and transcript information.')
                    else:
                        testimony = w.find('div',  {'class': 'mt-3'}).find("a")
                        if 'https:' in testimony["href"] or 'http:' in testimony["href"]:
                            res_tran = requests.get(testimony['href'], headers=headers)
                            soup_tran = BeautifulSoup(res_tran.text,'html.parser')
                            transcript_pdf = soup_tran.find("a", href=re.compile("download"))
                            
                            if transcript_pdf != None:
                                try:
                                    pdf_page = requests.get(transcript_pdf["href"], headers=headers)
                                    witness_url = pdf_page.url
                                    
                                except:
                                    witness_url = ""
                                    if "Closed" in d["Title"] or "RESCHEDULED" in d["Title"] or "POSTPONED" in d["Title"]:
                                        logging.error(f'{d["Title"]} at {d["Date"]} lacks witness and transcript information.')
                    
                    witness.append(witness_name)
                    transcripts.append(witness_url)
                    witness_transcripts.append((witness_name,witness_url))

                d["witnesses"] = witness
                d["transcripts"] = transcripts
                d["witness_transcripts"] = witness_transcripts
                                

        print(d)
    data_table = pd.DataFrame(data)
    print(data_table)
    
    return data_table

if os.path.exists("./SenateVideoFiles/Foreign.csv") == True:
    new_data = get_foreign_hearings(rows=0)
    old_data = pd.read_csv("./SenateVideoFiles/Foreign.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data[["Date","Time","URL","Title","Location","Committee","Date Scraped","video_url","witnesses","transcripts","witness_transcripts"]]
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("./SenateVideoFiles/Foreign.csv",  encoding='utf-8')
else: 
    get_foreign_hearings(rows=5000).to_csv("./SenateVideoFiles/Foreign.csv",  encoding='utf-8')
