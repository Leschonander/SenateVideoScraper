import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_intelligence_hearings():

    url = "https://www.intelligence.senate.gov/hearings"
    res = requests.get(url)

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
            "Location": ""
        }

        data.append(row_obj)
    
    for d in data:
        res_ind = requests.get(d["URL"])
        soup_ind = BeautifulSoup(res_ind.text,'html.parser')
        
        if soup_ind.find('iframe') == None:
            video_url = ""
        else:
            video_url =  soup_ind.find('iframe')["src"]
        
        d["video_url"] = video_url
    
    data_table = pd.DataFrame(data)
    print(data_table)

    return data_table

get_intelligence_hearings()