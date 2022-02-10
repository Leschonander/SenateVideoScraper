import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime

def get_veterans_hearings(rows: int):

    url = "https://www.veterans.senate.gov/hearings?c=all&maxrows=" + str(rows)
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
            date = date_time[0]
            time = date_time[1]
        
        if t.find('a', {'class': 'summary'}) == None:
            url = ""
            title = ""
        else:
            url = t.find('a', {'class': 'summary'})["href"].replace("\n", "").replace("\t", "")
            title = t.find('a', {'class': 'summary'}).get_text().replace("\n", "").replace("\t", "")
        

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
            
            if soup_ind.find('a', { 'id': 'watch-live-now'}) == None:
                video_url = ""
            else:
                video_url = "https://www.veterans.senate.gov" + soup_ind.find('a', { 'id': 'watch-live-now'})["href"].replace("javascript:openVideoWin('", "").replace("');", "")

            if soup_ind.findAll('span', {'class': 'fn'}) == None:
                d["witnesses"] = ""
            else:
                witness_html = soup_ind.findAll('span', {'class': 'fn'})
                witness_html = [w.get_text().replace("\t", "").replace("\n", " ").replace("0x80", "") for w in witness_html]
                # witness_html = [i for i in witness_html if "(" not in i]
                witness_html = [
                    w.replace("Hon.", "")
                     .replace("Mr.", "")
                     .replace("Ms.", "")
                     .replace("Mrs.", "")
                     .replace("Dr.", "")
                     .replace("Ph.D.", "")
                     .replace("PhD", "")
                     .replace("Ph.D", "")
                     .replace("MD", "")
                     .replace("M.D.", "")
                     .replace("MPH", "")
                     .replace("MSW", "")
                     .replace("Esq", "")
                     .replace("Esq.", "")
                     .replace("JD", "")
                     .replace("Senator", "")
                     .replace("Representative", "")
                     .replace("Lt", "")
                     .replace("The Honorable", "")
                     .replace("Honorable", "")
                     .replace("Ranking Member", "")
                     .replace("Chairman", "")
                     .replace("Chair", "")
                     .replace("USN", "")
                     .replace("USA", "")
                     .replace("USMC", "")
                     .replace("USN", "")
                     .replace("USCG", "")
                     .replace("USAF", "")
                     .replace("MACP", "")
                     .replace("(Ret)", "")
                     .replace(",", "")
                     .strip() 
                    for w in witness_html
                ]
                witness_html = [' '.join(w.split()) for w in witness_html]
                witness_html = list(set(witness_html))
                d["witnesses"] = witness_html
                
            d["video_url"] = video_url
        print(d)
    
    data_table = pd.DataFrame(data)
    print(data_table)

    return data_table

if os.path.exists("./SenateVideoFiles/Veterans.csv") == True:
    new_data = get_veterans_hearings(rows=10)
    old_data = pd.read_csv("./SenateVideoFiles/Veterans.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("./SenateVideoFiles/Veterans.csv",  encoding='utf-8')
else: 
    get_veterans_hearings(rows=5000).to_csv("./SenateVideoFiles/Veterans.csv",  encoding='utf-8')