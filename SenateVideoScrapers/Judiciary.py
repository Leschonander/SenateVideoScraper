import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime
import re

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
            
            if soup_ind.findAll('span', {'class': 'fn'}) == None:
                d["witnesses"] = ""
            else:
                witness_html = soup_ind.findAll('span', {'class': 'fn'})
                witness_html = [w.get_text().replace("\t", "").replace("\n", " ").replace("0x80", "") for w in witness_html]
                witness_html = [i for i in witness_html if "(" not in i]
                witness_html = [
                    w.replace("Hon.", "")
                     .replace("Mr.", "")
                     .replace("Ms.", "")
                     .replace("Mrs.", "")
                     .replace("Dr.", "")
                     .replace("Ph.D.", "")
                     .replace("PhD", "")
                     .replace("Senator", "")
                     .replace("Representative", "")
                     .replace("Lt", "")
                     .replace("The Honorable", "")
                     .replace("Ranking Member", "")
                     .replace("Chair", "")
                     .replace("Chairman", "")
                     .strip() 
                    for w in witness_html
                ]
                witness_html = [' '.join(w.split()) for w in witness_html]
                witness_html = list(set(witness_html))

                d["witnesses"] = witness_html

                transcripts = soup_ind.find_all("a", href=re.compile("testimony"))
                transcripts = [t["href"] for t in transcripts]
                transcript_links = []
                for t in transcripts:
                    res_tran = requests.get(t, headers=headers)
                    soup_tran = BeautifulSoup(res_tran.text,'html.parser')
                    transcript_pdf = soup_tran.find("a", href=re.compile("download"))
                    transcript_pdf = "http:" + transcript_pdf["href"]
                    try:
                        pdf_page = requests.get(transcript_pdf, headers=headers)
                        transcript_links.append(pdf_page.url)
                    except:
                        raise
                    
                
                d["transcripts"] = transcript_links
            
        d["video_url"] = video_url
        print(d)
    
    data_table = pd.DataFrame(data)
    return data_table

if os.path.exists("./SenateVideoFiles/Judiciary.csv") == True:
    new_data = get_judiciary_hearings(rows=10)
    old_data = pd.read_csv("./SenateVideoFiles/Judiciary.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("./SenateVideoFiles/Judiciary.csv",  encoding='utf-8')
else: 
    get_judiciary_hearings(rows=2000).to_csv("./SenateVideoFiles/Judiciary.csv",  encoding='utf-8')
