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


def get_intelligence_hearings(page: int):

    url = "https://www.intelligence.senate.gov/hearings?page=" + str(page)
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'https://github.com/Leschonander/SenateVideoScraper'  
    }
    res = requests.get(url, headers=headers)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('div', { 'class': 'views-row'})
    data = []
    for t in table_rows:
        date_time = t.find('div', {'class': 'views-field-field-hearing-date'}).get_text()
        if "-" in date_time:
            date_time_split = date_time.split("-")
            date = date_time_split[0].strip()
            time = date_time_split[1].strip()
        else:
            date = ""
            time = ""
        
        row_obj = {
            "Date": date,
            "Time": time,
            "URL": "https://www.intelligence.senate.gov/" + t.findAll("a")[0]["href"],
            "Title": t.findAll("a")[0].get_text().replace("\n", "").rstrip().replace("\t", ""),
            "Location": "",
            "Committee": "Intelligence",
            "Date Scraped": datetime.today().strftime("%Y-%m-%d")
        }

        data.append(row_obj)
    
    for d in data:
        if d["URL"] == "":
            d["video_url"] = ""
        else:
            res_ind = requests.get(d["URL"], headers=headers)
            soup_ind = BeautifulSoup(res_ind.text,'html.parser')
            
            if soup_ind.find('iframe') == None:
                video_url = ""
            else:
                video_url =  soup_ind.find('iframe')["src"]
            
            if soup_ind.findAll('div', {'class': 'entity'}) == None:
                d["witnesses"] = ""
                logging.error(f'{d["Title"]} at {d["Date"]} lacks witness and transcript information.')
            else:
                witness_cards = soup_ind.findAll("div", {"class": "entity"})
                witness = []
                transcripts = []
                witness_transcripts = []

                for w in witness_cards:

                    if w.find('div', {'class': 'field-name-field-witness-firstname'}) == None:
                        first_name = ""
                    else:
                        first_name = w.find('div', {'class': 'field-name-field-witness-firstname'}).get_text()
                    
                    if w.find('div', {'class': 'field-name-field-witness-lastname'}) == None:
                        last_name = ""
                    else:
                        last_name = w.find('div', {'class': 'field-name-field-witness-lastname'}).get_text()
                    
                    
                    witness_name = first_name + " " +last_name
                    witness_name = witness_name.replace("Hon.", "").replace("Mr.", "").replace("Ms.", "").replace("Mrs.", "").replace("Dr.", "").replace("Ph.D.", "").replace("PhD", "").replace("Senator", "").replace("Representative", "").replace("Lt", "").replace("The Honorable", "").replace("(R-GA)", "").strip() 
                    witness_name = ' '.join(witness_name.split())

                    if w.find("a", string=re.compile(r'Opening Statement|Response')) == None:
                        witness_url = ''
                        logging.error(f'{d["Title"]} at {d["Date"]} lacks a url for their testimony.')

                    else:
                        witness_url = w.find("a", string=re.compile(r'Opening Statement|Response'))
                        witness_url = "https://www.intelligence.senate.gov" + witness_url["href"]
                    
                    witness.append(witness_name)
                    transcripts.append(witness_url)
                    witness_transcripts.append((witness_name,witness_url))
                

                d["witnesses"] = witness
                d["transcripts"] = transcripts
                d["witness_transcripts"] = witness_transcripts

            
            d["video_url"] = video_url
            print(d)
    
    data_table = pd.DataFrame(data)

    return data_table

if os.path.exists("./SenateVideoFiles/Intelligence.csv") == True:
    pages = [i for i in range(1, 2)]
    data_table_list = []
    for p in pages:
        result = get_intelligence_hearings(p)
        print(result, p)
        data_table_list.append(result)
    new_data = pd.concat(data_table_list)

    old_data = pd.read_csv("./SenateVideoFiles/Intelligence.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("./SenateVideoFiles/Intelligence.csv",  encoding='utf-8')
else:

    pages = [i for i in range(0, 44)]
    data_table_list = []
    for p in pages:
        result = get_intelligence_hearings(p)
        print(result, p)
        data_table_list.append(result)

    data_table_list_master = pd.concat(data_table_list)
    data_table_list_master.to_csv("./SenateVideoFiles/Intelligence.csv",  encoding='utf-8')
