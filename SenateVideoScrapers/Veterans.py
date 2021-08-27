import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def get_veterans_hearings(rows: int):

    url = "https://www.veterans.senate.gov/hearings?c=all&maxrows=" + str(rows)
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
            "Committee": "Veterans"
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
            
            d["video_url"] = video_url
        print(d)
    
    data_table = pd.DataFrame(data)
    print(data_table)

    return data_table

if os.path.exists("../SenateVideoFiles/Veterans.csv") == True:
    new_data = get_veterans_hearings(rows=10)
    old_data = pd.read_csv("../SenateVideoFiles/Veterans.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("../SenateVideoFiles/Veterans.csv")
else: 
    get_veterans_hearings(rows=5000).to_csv("../SenateVideoFiles/Veterans.csv")