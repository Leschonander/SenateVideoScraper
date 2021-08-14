import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_armed_hearings():

    url = "https://www.armed-services.senate.gov/hearings"
    res = requests.get(url)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('tr', { 'class': 'vevent'})
    data = []
    for t in table_rows:
        date = t.find("time").get_text().split(" ")

        if  t.find("span", {'class': "location"}) == None:
            location = ""
        else:
            location =  t.find("span", {'class': "location"}).get_text().rstrip().lstrip()

        row_obj = {
            "Date": date[0],
            "Time": date[1],
            "URL": t.find("a")["href"].replace("\n", "").replace("\t", ""),
            "Title": t.find("a").get_text().replace("\n", "").replace("\t", "").rstrip(),
            "Location": location
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

get_armed_hearings()