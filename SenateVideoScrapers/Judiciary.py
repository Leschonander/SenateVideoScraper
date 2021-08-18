import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_judiciary_hearings():

    url = "https://www.judiciary.senate.gov/hearings?maxrows=2000"
    res = requests.get(url)

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
            "Committee": "Judiciary"
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
                video_url =  "https://www.judiciary.senate.gov" + soup_ind.find('a', { 'id': 'watch-live-now'})["href"].replace("javascript:openVideoWin('", "").replace("');", "")
            
        d["video_url"] = video_url
    
    data_table = pd.DataFrame(data)
    return data_table

get_judiciary_hearings().to_csv("../SenateVideoFiles/Judiciary.csv")