import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime
import re
import logging
import sentry_sdk
from sentry_sdk import capture_message
from sentry_sdk.integrations.logging import LoggingIntegration

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


def get_agricultural_hearings(rows: int):

    url = "https://www.agriculture.senate.gov/hearings?maxrows=" + str(rows)
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'https://github.com/Leschonander/SenateVideoScraper'  
    }
    res = requests.get(url, headers=headers)

    soup =  BeautifulSoup(res.text,'html.parser')
    
    
    table_rows = soup.findAll('div', { 'class': 'row'})
    data = []
    for t in table_rows:
        if t.find('time') == None:
            date = ""
            time = ""
        else:
            date_time = t.find('time').get_text().split("\n")
            date = date_time[1].strip()
            time = date_time[2].strip()
        
        if t.find('a', {'class': 'LegislationList__link'}) == None:
            url = ""
            title = ""
        else:
            url = t.find('a', {'class': 'LegislationList__link'})["href"]
            title = t.find('a', {'class': 'LegislationList__link'}).get_text().replace("\n", "").replace("\t", "").strip()
        
        if t.findAll("div", {'class': "col-md-3"}) == None:
            location = ""
            #print(t.findAll("div", {'class': "col-md-3"}))
        else:
            location = t.findAll("div", {'class': "col-md-3"})
            if len(location) != 2:
                location = ""
            else:
                location = t.findAll("div", {'class': "col-md-3"})[1].get_text().strip()
        
        row_obj = {
            "Date": date,
            "Time": time,
            "URL": url,
            "Title": title,
            "Location": location,
            "Committee": "Agriculture",
            "Date Scraped": datetime.today().strftime("%Y-%m-%d")
        }
        
        data.append(row_obj)
    
    for d in data:
        if d["URL"] == "":
            d["video_url"] = ""
        else:
            res_ind = requests.get(d["URL"], headers=headers)
            
            soup_ind = BeautifulSoup(res_ind.text,'html.parser')

            if soup_ind.findAll('li', {'class': 'col-md-6'}) == None:
                d["witnesses"] = ""
                d["transcripts"] = ""
                d["witness_transcripts"] = ""

                if "Closed" not in d["Title"] or "RESCHEDULED" not in d["Title"] or "POSTPONED" not in d["Title"]  or time.strptime(d["Date"], '%m/%d/%y') > datetime.today():
                    logging.error(f'{d["Title"]} at {d["Date"]} lacks witness and transcript information.')

            else:

                witness_cards = soup_ind.findAll("li", {"class": "col-md-6"})
                witness = []
                transcripts = []
                witness_transcripts = []

                for w in witness_cards:
                    witness_name = w.find('h4',  {'class': 'Heading__title'}).get_text().replace("\t", "").replace("\n", " ").replace("0x80", "").strip()
                    witness_name = witness_name.replace("Hon.", "").replace("Mr.", "").replace("Ms.", "").replace("Mrs.", "").replace("Dr.", "").replace("Ph.D.", "").replace("PhD", "").replace("Senator", "").replace("Representative", "").replace("Lt", "").replace("The Honorable", "").replace("(R-GA)", "").strip() 
                    witness_name = ' '.join(witness_name.split())

                    if w.find('a',  {'class': 'Button--hearingLink'}) == None:
                        witness_url = ''
                    else:
                        testimony = w.find('a',  {'class': 'Button--hearingLink'})
                        if 'https:' in testimony["href"] or 'http:' in testimony["href"]:
                            res_tran = requests.get(testimony['href'], headers=headers)
                            soup_tran = BeautifulSoup(res_tran.text,'html.parser')
                            transcript_pdf = soup_tran.find("a", href=re.compile("download"))
                            if transcript_pdf != None:
                                pdf_page = requests.get(transcript_pdf["href"], headers=headers)
                                witness_url = pdf_page.url
                            else:
                                witness_url = ''
                                logging.error(f'{d["Title"]} at {d["Date"]} lacks a url for their testimony.')

                    
                    witness.append(witness_name)
                    transcripts.append(witness_url)
                    witness_transcripts.append((witness_name,witness_url))

                d["witnesses"] = witness
                d["transcripts"] = transcripts
                d["witness_transcripts"] = witness_transcripts

               
            if soup_ind.find('iframe') == None:
                video_url = ""
            else:
                video_url =   soup_ind.find('iframe')['src']
            
            d["video_url"] = video_url
        print(d)
    data_table = pd.DataFrame(data)
    data_table = data_table.dropna(subset=["witnesses"])

    print(data_table)

    return data_table


if os.path.exists("./SenateVideoFiles/Agricultural.csv") == True:
    new_data = get_agricultural_hearings(rows=10)
    old_data = pd.read_csv("./SenateVideoFiles/Agricultural.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data[["Date","Time","URL","Title","Location","Committee","Date Scraped","video_url","witnesses","transcripts","witness_transcripts"]]
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("./SenateVideoFiles/Agricultural.csv",  encoding='utf-8')
else: 
    get_agricultural_hearings(rows=5000).to_csv("./SenateVideoFiles/Agricultural.csv",  encoding='utf-8')
