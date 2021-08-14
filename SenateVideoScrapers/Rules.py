import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_rules_hearings():

    url = "https://www.rules.senate.gov/hearings"
    res = requests.get(url)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('tr', { 'class': 'vevent'})
    data = []
    for t in table_rows:

        if t.find("time") == None:
            date = ""
            time = ""
        else:
            date_time = t.find("time").get_text().split(" ")
            date = date_time[0]
            time = date_time[1]
        
        if t.find("span", {'class': 'location'}) == None:
            location = ""
        else:
            location = t.find("span", {'class': 'location'}).get_text()

        row_obj = {
            "Date": date,
            "Time": time,
            "URL": "https://www.rules.senate.gov" + t.find("a", {'class': 'url'})["href"],
            "Title":  t.find("a", {'class': 'url'}).get_text().replace("\n", "").replace("\t", ""),
            "Location": location
        }

        data.append(row_obj)
    
    for d in data:
        res_ind = requests.get(d["URL"])
        soup_ind = BeautifulSoup(res_ind.text,'html.parser')
        if soup_ind.find('a', { 'id': 'watch-live-now'}) == None:
            video_url = ""
        else:
            video_url =  "https://www.rules.senate.gov" + soup_ind.find('a', { 'id': 'watch-live-now'})["href"].replace("javascript:openVideoWin('", "").replace("');", "")
        
        d["video_url"] = video_url
    
    data_table = pd.DataFrame(data)

    return data_table

get_rules_hearings()