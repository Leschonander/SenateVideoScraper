import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_foreign_hearings():

    url = "https://www.foreign.senate.gov/hearings"
    res = requests.get(url)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('tr', { 'class': 'vevent'})
    data = []
    for t in table_rows:
        date = t.findAll("time")[0].get_text().split(" ")
        try:
            time = date[1]
        except IndexError:
            time = ''
            
        row_obj = {
            "Date": date[0],
            "Time": time,
            "URL": "https://www.foreign.senate.gov/" + t.findAll("a")[0]["href"],
            "Title": t.find("td").get_text().replace("\n", "").replace("\t", ""),
            "Location": t.find("span", {'class': "location"}).get_text()
        }
        
        data.append(row_obj)
    
    for d in data:
        res_ind = requests.get(d["URL"])
        soup_ind = BeautifulSoup(res_ind.text,'html.parser')
        
        if soup_ind.find('iframe', { 'class': 'streaminghearing'}) == None:
            video_url = ""
        else:
            video_url =  soup_ind.find('iframe', { 'class': 'streaminghearing'})["src"]
        
        d["video_url"] = video_url
    
    data_table = pd.DataFrame(data)

    return data_table


get_foreign_hearings()