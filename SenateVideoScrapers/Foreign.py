import requests
from bs4 import BeautifulSoup
import pandas as pd
import os 

def get_foreign_hearings(rows: int):

    url = "https://www.foreign.senate.gov/hearings?maxrows=" + str(rows)
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
            except IndexError:
                time = ""
        
        if t.find('a', {'class': 'summary'}) == None:
            url = ""
            title = ""
        else:
            url = "https://www.foreign.senate.gov" + t.find('a', {'class': 'summary'})["href"]
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
            "Committee": "Foreign"
        }
        
        data.append(row_obj)
    
    for d in data:
        if d["URL"] == "":
            d["video_url"] = ""
        else:
            res_ind = requests.get(d["URL"])
            soup_ind = BeautifulSoup(res_ind.text,'html.parser')
            
            if soup_ind.find('iframe', { 'class': 'streaminghearing'}) == None:
                video_url = ""
            else:
                video_url =  soup_ind.find('iframe', { 'class': 'streaminghearing'})["src"]
            
            d["video_url"] = video_url
        print(d)
    data_table = pd.DataFrame(data)
    print(data_table)
    
    return data_table

if os.path.exists("./SenateVideoFiles/Finance.csv") == True:
    new_data = get_foreign_hearings(rows=20)
    old_data = pd.read_csv("../SenateVideoFiles/Finance.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("../SenateVideoFiles/Finance.csv")
else: 
    get_foreign_hearings(rows=5000).to_csv("../SenateVideoFiles/Foreign.csv")