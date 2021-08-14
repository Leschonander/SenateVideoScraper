import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_enviroment_hearings():

    url = "https://www.epw.senate.gov/public/index.cfm/hearings"
    res = requests.get(url)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('tr')
    data = []
    for t in table_rows:
        
        if t.findAll("td") == []:
            continue
        else:
            # print(t.find("td", {'class': 'recordListDate'}))
            row_obj = {
                "Date": t.find("td", {'class': 'recordListDate'}).get_text(),
                "Time": t.find("td", {'class': 'recordListTime'}).get_text(),
                "URL": "https://www.epw.senate.gov" + t.find("a")["href"],
                "Title": "https://www.epw.senate.gov/" + t.find("a").get_text(),
                "Location": ""
            }

            data.append(row_obj)
    
    for d in data:
        res_ind = requests.get(d["URL"])
        soup_ind = BeautifulSoup(res_ind.text,'html.parser')

        if soup_ind.find('iframe', { 'class': 'embed-responsive-item'}) == None:
            video_url = ""
        else:
            video_url =  soup_ind.find('iframe', { 'class': 'embed-responsive-item'})["src"]
        
        d["video_url"] = video_url
    
    data_table = pd.DataFrame(data)

    return data_table

get_enviroment_hearings()