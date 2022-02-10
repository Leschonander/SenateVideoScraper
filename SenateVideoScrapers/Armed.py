import requests
from bs4 import BeautifulSoup
import pandas as pd
import os 
from datetime import datetime


def get_armed_hearings(rows: int):

    url = "https://www.armed-services.senate.gov/hearings?c=all&maxrows=" + str(rows)
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'https://github.com/Leschonander/SenateVideoScraper'  
    }
    res = requests.get(url, headers=headers)

    soup =  BeautifulSoup(res.text,'html.parser')

    table_rows = soup.findAll('tr', { 'class': 'vevent'})
    data = []
    for t in table_rows:
        if t.find("time").get_text() == None:
            date = ["", ""]
        else:
            date = t.find("time").get_text().split(" ")
        
        if  t.find("a") == None:
            url = ""
            title = ""
        else:
            url = t.find("a")["href"].replace("\n", "").replace("\t", "")
            title = t.find("a").get_text().replace("\n", "").replace("\t", "").rstrip()

        if  t.find("span", {'class': "location"}) == None:
            location = ""
        else:
            location =  t.find("span", {'class': "location"}).get_text().rstrip().lstrip()
        
        

        row_obj = {
            "Date": date[0],
            "Time": date[1],
            "URL": url,
            "Title": title,
            "Location": location,
            "Committee": "Armed",
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
                video_url =  soup_ind.find('a', { 'id': 'watch-live-now'})["href"].replace("javascript:openVideoWin('", "").replace("');", "")
            
            if soup_ind.findAll('span', {'class': 'fn'}) == None:
                d["witnesses"] = ""
            else:
                witness_html = soup_ind.findAll('span', {'class': 'fn'})
                witness_html = [w.get_text().replace("\t", "").replace("\n", " ").replace("0x80", "")  for w in witness_html]
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
                     .replace(", USN", "")
                     .replace(", USA", "")
                     .replace(", USMC", "")
                     .replace(", USN", "")
                     .replace(", USCG", "")
                     .replace(", USAF", "")
                     .replace("**", "")
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

if os.path.exists("./SenateVideoFiles/Armed.csv") == True:
    new_data = get_armed_hearings(rows=20)
    old_data = pd.read_csv("./SenateVideoFiles/Armed.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("./SenateVideoFiles/Armed.csv",  encoding='utf-8')
else: 
    get_armed_hearings(rows=5000).to_csv("./SenateVideoFiles/Armed.csv",  encoding='utf-8')


