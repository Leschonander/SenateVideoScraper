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

        date = t.findAll("td")[2].get_text().split(" ")
        row_obj = {
            "Date": date[0].replace("\n", ""),
            "Time": date[1].replace("\n", ""),
            "URL": "https://www.judiciary.senate.gov/" + t.findAll("a")[0]["href"],
            "Title": t.findAll("a")[0].get_text().replace("\n", "").rstrip().replace("\t", ""),
            "Location": t.findAll("td")[2].get_text().replace("\n", "").replace("\t", ""),
            "Committee": "Judiciary"
        }
        
        data.append(row_obj)
    
    for d in data:
        res_ind = requests.get(d["URL"])
        soup_ind = BeautifulSoup(res_ind.text,'html.parser')
        if soup_ind.find('a', { 'id': 'watch-live-now'}) == None:
            video_url = ""
        else:
            video_url =  soup_ind.find('a', { 'id': 'watch-live-now'})["href"].replace("javascript:openVideoWin('", "").replace("');", "")
        
        d["video_url"] = video_url
    
    data_table = pd.DataFrame(data)

    return data_table

get_judiciary_hearings().to_csv("ex_jud.csv")