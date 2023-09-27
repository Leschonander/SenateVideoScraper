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


def get_health_hearings(rows: int):

    url = "https://www.help.senate.gov/hearings?maxrows=" + str(rows)
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'https://github.com/Leschonander/SenateVideoScraper'  
    }
    res = requests.get(url, headers=headers)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('div', { 'class': 'LegislationList__item'})
    data = []
    for t in table_rows:
        
        if t.find("time") == None:
            date = ["", ""]
        else:
            date = t.find("time")["datetime"]
            time = t.find("time").find('span', class_='sr-only', string='Time:').next_sibling.strip()
        
        if  t.find("a") == None:
            url = ""
            title = ""
        else:
            url = t.find("a")["href"].replace("\n", "").replace("\t", "")
            title = t.find("a").get_text().replace("\n", "").replace("\t", "").strip()

        if  t.find("div", {'class': "LegislationList__locationCol"}) == None:
            location = ""
        else:
            location =  t.find("div", {'class': "LegislationList__locationCol"}).get_text().rstrip().lstrip()
        
        row_obj = {
            "Date": date,
            "Time": time,
            "URL": url,
            "Title": title,
            "Location": location,
            "Committee": "Health",
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
                video_url =  "https://www.help.senate.gov" + soup_ind.find('a', { 'id': 'watch-live-now'})["href"].replace("javascript:openVideoWin('", "").replace("');", "")
            
            if soup_ind.findAll('div', {'class': 'Hearing__orderedListBullet'}) == None:
                d["witnesses"] = ""
                d["transcripts"] = ""
                d["witness_transcripts"] = ""
                if "Closed" in d["Title"] or "RESCHEDULED" in d["Title"] or "POSTPONED" in d["Title"]  or datetime.strptime(d["Date"], "%m/%d/%y") > datetime.today():
                    logging.error(f'{d["Title"]} at {d["Date"]} lacks witness and transcript information.')

            else:
                witness_cards = soup_ind.findAll("div", {"class": "Hearing__orderedListBullet"})
                witness = []
                transcripts = []
                witness_transcripts = []

                for w in witness_cards:
                    witness_name = w.find('h3',  {'class': 'Heading__title'}).get_text().replace("\t", "").replace("\n", " ").replace("0x80", "").strip()
                    witness_name = witness_name.replace("Hon.", "").replace("Mr.", "").replace("Ms.", "").replace("Mrs.", "").replace("Dr.", "").replace("Ph.D.", "").replace("PhD", "").replace("Senator", "").replace("Representative", "").replace("Lt", "").replace("The Honorable", "").replace("(R-GA)", "").strip() 
                    witness_name = ' '.join(witness_name.split())

                    if w.find('div',  {'class': 'mt-3'}) == None:
                        witness_url = ''
                        logging.error(f'{d["Title"]} at {d["Date"]} lacks a url for their testimony.')
                    else:
                        testimony = w.find('div',  {'class': 'mt-3'}).find("a")
                        if ('https:' in testimony["href"] or 'http:' in testimony["href"]) and "https://www.help.senate.gov" in testimony["href"]:
                            res_tran = requests.get(testimony['href'], headers=headers)
                            soup_tran = BeautifulSoup(res_tran.text,'html.parser')
                            transcript_pdf = soup_tran.find("a", href=re.compile("download"))
                            if transcript_pdf != None:
                                try:
                                    pdf_page = requests.get(transcript_pdf["href"], headers=headers)
                                    witness_url = pdf_page.url
                                except:
                                    witness_url = ""
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

if os.path.exists("./SenateVideoFiles/Health.csv") == True:
    new_data = get_health_hearings(rows=10)
    old_data = pd.read_csv("./SenateVideoFiles/Health.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data[["Date","Time","URL","Title","Location","Committee","Date Scraped","video_url","witnesses","transcripts","witness_transcripts"]]
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("./SenateVideoFiles/Health.csv",  encoding='utf-8')
else: 
    get_health_hearings(rows=4000).to_csv("./SenateVideoFiles/Health.csv",  encoding='utf-8')