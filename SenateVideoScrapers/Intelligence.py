import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def get_intelligence_hearings(page: int):

    url = "https://www.intelligence.senate.gov/hearings?page=" + str(page)
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'https://github.com/Leschonander/SenateVideoScraper'  
    }
    res = requests.get(url, headers=headers)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('div', { 'class': 'views-row'})
    data = []
    for t in table_rows:
        date_time = t.find('div', {'class': 'views-field-field-hearing-date'}).get_text()
        if "-" in date_time:
            date_time_split = date_time.split("-")
            date = date_time_split[0].strip()
            time = date_time_split[1].strip()
        else:
            date = ""
            time = ""
        
        row_obj = {
            "Date": date,
            "Time": time,
            "URL": "https://www.intelligence.senate.gov/" + t.findAll("a")[0]["href"],
            "Title": t.findAll("a")[0].get_text().replace("\n", "").rstrip().replace("\t", ""),
            "Location": "",
            "Committee": "Intelligence"
        }

        data.append(row_obj)
    
    for d in data:
        if d["URL"] == "":
            d["video_url"] = ""
        else:
            res_ind = requests.get(d["URL"])
            soup_ind = BeautifulSoup(res_ind.text,'html.parser')
            
            if soup_ind.find('iframe') == None:
                video_url = ""
            else:
                video_url =  soup_ind.find('iframe')["src"]
            
            d["video_url"] = video_url
    
    data_table = pd.DataFrame(data)

    return data_table

if os.path.exists("./SenateVideoFiles/Intelligence.csv") == True:
    pages = [i for i in range(1, 2)]
    data_table_list = []
    for p in pages:
        result = get_intelligence_hearings(p)
        print(result, p)
        data_table_list.append(result)
    new_data = pd.concat(data_table_list)

    old_data = pd.read_csv("./SenateVideoFiles/Intelligence.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("./SenateVideoFiles/Intelligence.csv")
else:

    pages = [i for i in range(0, 44)]
    data_table_list = []
    for p in pages:
        result = get_intelligence_hearings(p)
        print(result)
        data_table_list.append(result)

    data_table_list_master = pd.concat(data_table_list)
    data_table_list_master.to_csv("./SenateVideoFiles/Intelligence.csv")
