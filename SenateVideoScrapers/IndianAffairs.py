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

def get_indian_affairs_hearings(page: int):

    url = "https://www.indian.senate.gov/hearings?page=" + str(page)
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'https://github.com/Leschonander/SenateVideoScraper'  
    }
    res = requests.get(url, headers=headers)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('tr')
    table_rows = table_rows[1:]
    data = []
    for t in table_rows:

        if  t.find("td", {'class': "views-field-field-hearing-new-office"}) == None:
            location = ""
        else:
            location = t.find("td", {'class': "views-field-field-hearing-new-office"}).get_text().rstrip().lstrip()
        
        if t.find("span", {'class': "date-display-single"}) == None:
            date = ""
        else:
            date = t.find("span", {'class': "date-display-single"}).get_text().replace("\n", "")
            date =  datetime.strptime(date, '%b %d, %Y').strftime("%m/%d/%Y")

        row_obj = {
            "Date":date,
            "Time": t.findAll("span", {'class': "date-display-single"})[1].get_text(),
            "URL": "https://www.indian.senate.gov/" + t.findAll("a")[0]["href"],
            "Title": t.findAll("a")[0].get_text().replace("\n", "").rstrip().replace("\t", ""),
            "Location": location,
            "Committee": "Indian Affairs",
            "Date Scraped": datetime.today().strftime("%Y-%m-%d")
        }
        data.append(row_obj)
    
    for d in data:
        res_ind = requests.get(d["URL"], headers=headers)
        soup_ind = BeautifulSoup(res_ind.text,'html.parser')
        if soup_ind.find('div', { 'class': 'field-name-field-hearing-new-video'}) == None:
            video_url  = ""
        else:
            video_div = soup_ind.find('div', { 'class': 'field-name-field-hearing-new-video'})

            if video_div.find('iframe') == None:
                video_url = ""
            else:
                video_url =  video_div.find('iframe')["src"]

            if soup_ind.findAll('div', {'class': 'field-item'}) == None:
                d["witnesses"] = ""
                d["transcripts"] = ""
                d["witness_transcripts"] = ""
                if "Closed" in d["Title"] or "RESCHEDULED" in d["Title"] or "POSTPONED" in d["Title"]  or time.strptime(d["Date"], '%m/%d/%y') > datetime.today():
                    logging.error(f'{d["Title"]} at {d["Date"]} lacks witness and transcript information.')
            else:
                witness_cards = soup_ind.findAll('div', {'class': 'field-item'})
                witness = []
                transcripts = []
                witness_transcripts = []

                for w in witness_cards:
                    if w.find('div',  {'class': 'group-header'}) == None:
                        witness_name = ''
                    else: 
                        witness_name = w.find('div',  {'class': 'group-header'}).get_text().replace("\t", "").replace("\n", " ").replace("0x80", "").strip()
                        witness_name = witness_name.replace("Hon.", "").replace("Mr.", "").replace("Ms.", "").replace("Mrs.", "").replace("Dr.", "").replace("Ph.D.", "").replace("PhD", "").replace("Senator", "").replace("Representative", "").replace("Lt", "").replace("The Honorable", "").replace("(R-GA)", "").strip() 
                        witness_name = ' '.join(witness_name.split())

                    if w.find('a', string=re.compile(r'Testimony')) == None:
                        witness_url = ''
                        logging.error(f'{d["Title"]} at {d["Date"]} lacks a url for their testimony.')
                    else:
                        link = w.find('a', string=re.compile(r'Testimony'))
                        url_not_present = re.compile("http(s)?://www.indian.senate.gov|http://indian.senate.gov").search(link["href"]) == None
                        if url_not_present == True:
                            witness_url = "https://www.indian.senate.gov" + link["href"]
                        else:
                            witness_url = link["href"]
                    witness.append(witness_name)
                    transcripts.append(witness_url)
                    witness_transcripts.append((witness_name,witness_url))
                
                d["witnesses"] = witness
                d["transcripts"] = transcripts
                d["witness_transcripts"] = witness_transcripts
            
        print(d)
        d["video_url"] = video_url

    data_table = pd.DataFrame(data)
    
    return data_table

if os.path.exists("./SenateVideoFiles/IndianAffairs.csv") == True:
    pages = [i for i in range(1, 2)]
    data_table_list = []
    for p in pages:
        result = get_indian_affairs_hearings(p)
        print(result, p)
        data_table_list.append(result)
    new_data = pd.concat(data_table_list)

    old_data = pd.read_csv("./SenateVideoFiles/IndianAffairs.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data[["Date","Time","URL","Title","Location","Committee","Date Scraped","video_url","witnesses","transcripts","witness_transcripts"]]
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("./SenateVideoFiles/IndianAffairs.csv",  encoding='utf-8')

else:
    pages = [i for i in range(0, 49)] #0 ,49
    data_table_list = []
    for p in pages:
        result = get_indian_affairs_hearings(p)
        print(result, p)
        data_table_list.append(result)

    data_table_list_master = pd.concat(data_table_list)
    data_table_list_master.to_csv("./SenateVideoFiles/IndianAffairs.csv",  encoding='utf-8')
