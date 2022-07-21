import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime
import re
from urllib.parse import urlparse
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

def get_judiciary_hearings(rows: int):

    url = "https://www.judiciary.senate.gov/hearings?maxrows=" + str(rows)
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'https://github.com/Leschonander/SenateVideoScraper'  
    }
    res = requests.get(url, headers=headers)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('tr', { 'class': 'vevent'})
    data = []
    for t in table_rows:

        if t.find('time', {'class': 'dtstart'}) == None:
            date = ""
            time = ""
        else:
            date_time = t.find('time', {'class': 'dtstart'}).get_text().split(" ")
            
            try:
                date = date_time[0]
            except:
                date = ""

            try:
                time = date_time[1]
            except:
                time = ""

        if t.find('a') == None:
            url = ""
            title = ""
        else:
            url = "https://www.judiciary.senate.gov" + t.find('a')["href"]
            title = t.find('a').get_text().strip()

        if t.find('span', {'class': 'location'}) == None:
            location = ""
        else:
            location =  t.find('span', {'class': 'location'}).get_text()
        

        row_obj = {
            "Date": date,
            "Time": time,
            "URL": url,
            "Title": title,
            "Location": location,
            "Committee": "Judiciary",
            "Date Scraped": datetime.today().strftime("%Y-%m-%d")
        }
        data.append(row_obj)
    
    for d in data:
        if d["URL"] == "":
            d["video_url"] = ""
        else:
            res_ind = requests.get(d["URL"], headers=headers)
            soup_ind = BeautifulSoup(res_ind.text,'html.parser')
            if soup_ind.find('a', { 'id': 'watch-live-now'}) == None:
                video_url = ""
            else:
                video_url =  "https://www.judiciary.senate.gov" + soup_ind.find('a', { 'id': 'watch-live-now'})["href"].replace("javascript:openVideoWin('", "").replace("');", "")
            
            if soup_ind.findAll('div', {'class': 'vcard'}) == None:
                d["witnesses"] = ""
                d["transcripts"] = ""
                d["witness_transcripts"] = ""
                if "Closed" in d["Title"] or "RESCHEDULED" in d["Title"] or "POSTPONED" in d["Title"]  or time.strptime(d["Date"], '%m/%d/%y') > datetime.today():
                    logging.error(f'{d["Title"]} at {d["Date"]} lacks witness and transcript information.')

            else:
                witness_cards = soup_ind.findAll("div", {"class": "vcard"})
                witness = []
                transcripts = []
                witness_transcripts = []

                for w in witness_cards:

                    if  w.find('span',  {'class': 'fn'}) == None:
                        witness_name = ''
                    else: 
                        witness_name = w.find('span',  {'class': 'fn'}).get_text().replace("\t", "").replace("\n", " ").replace("0x80", "").strip()
                        witness_name = witness_name.replace("Hon.", "").replace("Mr.", "").replace("Ms.", "").replace("Mrs.", "").replace("Dr.", "").replace("Ph.D.", "").replace("PhD", "").replace("Senator", "").replace("Representative", "").replace("Lt", "").replace("The Honorable", "").replace("(R-GA)", "").strip() 
                        witness_name = ' '.join(witness_name.split())

                    if w.find('a',  {'class': 'hearing-pdf'}) == None:
                        witness_url = ''
                        logging.error(f'{d["Title"]} at {d["Date"]} lacks a url for their testimony.')
                    else:
                        testimony = w.find('a',  {'class': 'hearing-pdf'})
                        if ('https:' in testimony["href"] or 'http:' in testimony["href"]):
                            try:
                                res_tran = requests.get(testimony['href'], headers=headers)
                            except:
                                witness_url = ""
                                logging.error(f'{d["Title"]} at {d["Date"]} lacks a url for their testimony.')
                            res_tran = requests.get(testimony['href'], headers=headers)
                            soup_tran = BeautifulSoup(res_tran.text,'html.parser')
                            transcript_pdf = soup_tran.find("a", href=re.compile("download"))
                            if transcript_pdf != None:
                                try:
                                    pdf_page = requests.get("https:" + transcript_pdf["href"], headers=headers)
                                    witness_url = pdf_page.url
                                except:
                                    witness_url = ""
                                    if d["Time"].strptime(d["Date"], '%m/%d/%y') > datetime.today():
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
    return data_table

if os.path.exists("./SenateVideoFiles/Judiciary.csv") == True:
    new_data = get_judiciary_hearings(rows=10)
    old_data = pd.read_csv("./SenateVideoFiles/Judiciary.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data[["Date","Time","URL","Title","Location","Committee","Date Scraped","video_url","witnesses","transcripts","witness_transcripts"]]
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("./SenateVideoFiles/Judiciary.csv",  encoding='utf-8')
else: 
    get_judiciary_hearings(rows=2000).to_csv("./SenateVideoFiles/Judiciary.csv",  encoding='utf-8')
