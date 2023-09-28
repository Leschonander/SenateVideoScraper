import requests
from bs4 import BeautifulSoup
import pandas as pd
import os 
from datetime import datetime
from dotenv import load_dotenv
import logging
import re
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


def get_homeland_security_hearings(page: int):

    url = f"https://www.hsgac.senate.gov/hearings?PageNum_rs={page}&c=all"
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'https://github.com/Leschonander/SenateVideoScraper'  
    }
    res = requests.get(url, headers=headers)
    
    soup =  BeautifulSoup(res.text,'html.parser')
    
    table_rows = soup.findAll('div', { 'class': 'jet-listing-grid__item'})
    data = []
    for t in table_rows:
        
        date =  t.findAll('div', {'class': 'jet-listing-dynamic-field__content'})[1].get_text().strip()
        time = t.findAll('div', {'class': 'jet-listing-dynamic-field__content'})[2].get_text().strip()
        
        if t.find('h3') == None:
            url = ""
            title = ""
        else:
            if t.find('h3').find("a") == None:
                url = ""
            else:
                url =  t.find('h3').find("a")["href"]
            title = t.find('h3').get_text().replace("\n", "").replace("\t", "").strip()

        if t.find('div', {'class': 'jet-listing-dynamic-field__content'}) == None:
            location = ""
        else:
            
            location =  t.find('div', {'class': 'jet-listing-dynamic-field__content'}).get_text()
        
        row_obj = {
            "Date": date,
            "Time": time,
            "URL": url,
            "Title": title,
            "Location": location,
            "Committee": "Homeland Security",
            "Date Scraped": datetime.today().strftime("%Y-%m-%d")
        }

        data.append(row_obj)
    
    for d in data:
        print(d)
        if d["URL"] == "":
            video_url = ""
        else:
            res_ind = requests.get(d["URL"], headers=headers)
            soup_ind = BeautifulSoup(res_ind.text,'html.parser')

            if soup_ind.find('a', { 'id': 'watch-live-now'}) == None:
                video_url = ""
            else:
                video_url =  soup_ind.find('a', { 'id': 'watch-live-now'})["href"].replace("javascript:openVideoWin('", "").replace("');", "")

            if soup_ind.find("div", {"class": "elementor-container"}) == None:
                d["witnesses"] = ""
                d["transcripts"] = ""
                d["witness_transcripts"] = ""
                
                # if "Closed" in d["Title"] or "RESCHEDULED" in d["Title"] or "POSTPONED" in d["Title"]  or datetime.strptime(d["Date"], "%m/%d/%y") > datetime.today():
                #   logging.error(f'{d["Title"]} at {d["Date"]} lacks witness and transcript information.')

            else:
                people_list = soup_ind.find("div", {"class": "elementor-container"}, re.compile('DOWNLOAD TESTIMONY'))# soup_ind.find("div", {"class": "elementor-widget-wrap"}, text = re.compile('DOWNLOAD TESTIMONY'))
                print(people_list.parent)
                witness_cards = people_list.findAll("li")
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
                    else:
                        testimony = w.find('a',  {'class': 'hearing-pdf'})
                        if 'https:' in testimony["href"] or 'http:' in testimony["href"]:
                            try:
                                pdf_page = requests.get(testimony["href"], headers=headers)
                                witness_url = pdf_page.url
                            except:
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

    return data_table
        
if os.path.exists("./SenateVideoFiles/HomeLandSecurity.csv") == True:
    pages = [i for i in range(1, 2)]
    data_table_list = []
    for p in pages:
        result = get_homeland_security_hearings(p)
        print(result, p)
        data_table_list.append(result)
    new_data = pd.concat(data_table_list)

    old_data = pd.read_csv("./SenateVideoFiles/HomeLandSecurity.csv",  lineterminator='\n')
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data[["Date","Time","URL","Title","Location","Committee","Date Scraped","video_url","witnesses","transcripts","witness_transcripts"]]
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("./SenateVideoFiles/HomeLandSecurity.csv",  encoding='utf-8')

else: 
    pages = [i for i in range(1, 96)]
    data_table_list = []
    for p in pages:
        result = get_homeland_security_hearings(p)
        print(result, p)
        data_table_list.append(result)

    data_table_list_master = pd.concat(data_table_list)
    data_table_list_master.to_csv("./SenateVideoFiles/HomeLandSecurity.csv",  encoding='utf-8')
