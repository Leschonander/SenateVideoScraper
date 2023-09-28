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

def get_veterans_hearings(rows: int):

    url = "https://www.veterans.senate.gov/hearings?c=all&maxrows=" + str(rows)
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'https://github.com/Leschonander/SenateVideoScraper'  
    }
    res = requests.get(url, headers=headers)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('div', { 'class': 'hearing-list-item'})
    data = []
    for t in table_rows:
        if t.find('span', {'class': 'hearing-list-datetime'}) == None:
            date = ""
            time = ""
        else:
            date = t.find('strong').get_text().strip()
            time = t.find("span", {'class': 'hearing-list-datetime'}).get_text().replace("\n", "").replace("\t", "").strip().replace(" ", "").split("\r")[1]
        
        if t.find('a') == None:
            url = ""
        else:
            url = t.find('a')["href"]

        if t.find('div', {'class': "hearing-list-title"}) == None:
            title = ""
        else:
            title = t.find('div', {'class': "hearing-list-title"}).get_text()

        location = "not on this page"
        
        row_obj = {
            "Date": date,
            "Time": time,
            "URL": url,
            "Title": title,
            "Location": location,
            "Committee": "Veterans",
            "Date Scraped": datetime.today().strftime("%Y-%m-%d")
        }

        data.append(row_obj)
    
    for d in data:
        if d["URL"] == "":
            d["video_url"] = ""
        else:
            res_ind = requests.get(d["URL"])
            soup_ind = BeautifulSoup(res_ind.text,'html.parser')

            d["Location"] = soup_ind.find('span', {'class': "hearing-event-details"}).get_text().replace("\n", "").strip()
            
            if soup_ind.find('a', { 'id': 'watch-live-now'}) == None:
                video_url = ""
            else:
                video_url = "https://www.veterans.senate.gov" + soup_ind.find('a', { 'id': 'watch-live-now'})["href"].replace("javascript:openVideoWin('", "").replace("');", "")
            if soup_ind.findAll('li', {'class': 'hearing-statement'}) == None:
                d["witnesses"] = ""
                d["transcripts"] = ""
                d["witness_transcripts"] = ""
                if "Closed" in d["Title"] or "RESCHEDULED" in d["Title"] or "POSTPONED" in d["Title"]  or time.strptime(d["Date"], '%m/%d/%y') > datetime.today():
                    logging.error(f'{d["Title"]} at {d["Date"]} lacks witness and transcript information.')
            else:
                witness_cards = soup_ind.findAll("li", {"class": "hearing-statement"})

                witness = []
                transcripts = []
                witness_transcripts = []

                for w in witness_cards:
                    
                    witness_name = w.find('h4',  {'class': 'full-name'}).get_text().replace("\t", "").replace("\n", " ").replace("0x80", "").strip()
                    witness_name = witness_name.replace("Hon.", "").replace("Mr.", "").replace("Ms.", "").replace("Mrs.", "").replace("Dr.", "").replace("Ph.D.", "").replace("PhD", "").replace("Ph.D", "").replace("MD", "").replace("M.D.", "").replace("MPH", "").replace("MSW", "").replace("Esq", "").replace("Esq.", "").replace("JD", "").replace("Senator", "").replace("Representative", "").replace("Lt", "").replace("The Honorable", "").replace("Honorable", "").replace("Ranking Member", "").replace("Chairman", "").replace("Chair", "").replace("USN", "").replace("USA", "").replace("USMC", "").replace("USN", "").replace("USCG", "").replace("USAF", "").replace("MACP", "").replace("(Ret)", "").replace(",", "").strip() 
                    witness_name = ' '.join(witness_name.split())
                    
                    if w.find('a') == None:
                        witness_url = ''
                        logging.error(f'{d["Title"]} at {d["Date"]} lacks a url for their testimony.')
                    else:
                        testimony = w.find('a')
                        if 'https:' in testimony["href"] or 'http:' in testimony["href"]:
                            res_tran = requests.get(testimony['href'], headers=headers)
                            witness_url = res_tran.url
                        else:
                            witness_url = ''
                            logging.error(f'{d["Title"]} at {d["Date"]} lacks a url for their testimony.')
                    
                    witness.append(witness_name)
                    transcripts.append(witness_url)
                    witness_transcripts.append((witness_name,witness_url))
                    
                d["witnesses"] = witness
                d["transcripts"] = transcripts
                d["witness_transcripts"] = witness_transcripts

            d["video_url"] = video_url
        print(d)
    
    data_table = pd.DataFrame(data)
    print(data_table)

    return data_table

if os.path.exists("./SenateVideoFiles/Veterans.csv") == True:
    new_data = get_veterans_hearings(rows=10)
    old_data = pd.read_csv("./SenateVideoFiles/Veterans.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data[["Date","Time","URL","Title","Location","Committee","Date Scraped","video_url","witnesses","transcripts","witness_transcripts"]]
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("./SenateVideoFiles/Veterans.csv",  encoding='utf-8')
else: 
    get_veterans_hearings(rows=5000).to_csv("./SenateVideoFiles/Veterans.csv",  encoding='utf-8')