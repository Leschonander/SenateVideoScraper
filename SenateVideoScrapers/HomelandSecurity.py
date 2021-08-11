import requests
from bs4 import BeautifulSoup
import pandas as pd

# Instead of getting all at once we can just filter for the ones from today when 
# populating whatever backend

def get_homeland_security_hearings():

    url = "https://www.hsgac.senate.gov/hearings"
    res = requests.get(url)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('tr', { 'class': 'vevent'})
    data = []
    for t in table_rows:
        date = t.findAll("td")[0].get_text().split(" ")
        row_obj = {
            "Date": date[0],
            "Time": date[1],
            "URL": t.findAll("a")[0]["href"],
            "Title": t.findAll("a")[0].get_text(),
            "Location": t.findAll("td")[2].get_text().replace("\n", "")
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

    data_table.to_csv("ex.csv")
        

get_homeland_security_hearings()