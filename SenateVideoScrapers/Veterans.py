import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_veterans_hearings():

    url = "https://www.veterans.senate.gov/hearings?c=all"
    res = requests.get(url)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('tr', { 'class': 'vevent'})
    data = []
    for t in table_rows:

        date_time = t.find('time', {'class': 'dtstart'}).get_text().split(" ")

        row_obj = {
            "Date":date_time[0],
            "Time": date_time[1],
            "URL": t.find('a', {'class': 'summary'})["href"].replace("\n", "").replace("\t", ""),
            "Title": t.find('a', {'class': 'summary'}).get_text().replace("\n", "").replace("\t", ""),
            "Location": t.find('td', {'class': 'location'}).get_text().replace("\n", "").replace("\t", "").replace("Location", "")
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
    
    data_table = pd.DataFrame(data)
    print(data_table)

    return data_table


get_veterans_hearings()