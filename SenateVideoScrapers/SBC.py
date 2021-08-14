import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_SBC_hearings():

    url = "https://www.sbc.senate.gov/public/index.cfm/hearings?MonthDisplay=0&YearDisplay=0"
    res = requests.get(url)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('tr')
    data = []
    for t in table_rows:
        if t.find("td", {'class': 'recordListDate'}) == None:
            date = ""
        else:
            date = t.find("td", {'class': 'recordListDate'}).get_text()

        if t.find("td", {'class': 'recordListTime'}) == None:
            time = ""
        else:
            time = t.find("td", {'class': 'recordListTime'}).get_text()
        
        if t.find("td", {'class': 'recordListTitle'}) == None:
            url = ""
            title = ""
        else:
            url = "https://www.sbc.senate.gov" + t.find("td", {'class': 'recordListTitle'}).find('a')['href']
            title = t.find("td", {'class': 'recordListTitle'}).find('a').get_text()

        row_obj = {
            "Date": date,
            "Time": time,
            "URL": url,
            "Title": title,
            "Location": ""
        }

        data.append(row_obj)
    
    for d in data:
        if d["URL"] == "":
            d["video_url"] = ""
        else:
            res_ind = requests.get(d["URL"])
            soup_ind = BeautifulSoup(res_ind.text,'html.parser')
            
            if soup_ind.find('iframe', { 'class': 'embed-responsive-item'}) == None:
                video_url = ""
            else:
                video_url =  soup_ind.find('iframe', { 'class': 'embed-responsive-item'})["src"]
        
            d["video_url"] = video_url
    
    data_table = pd.DataFrame(data)
    print(data_table)

    return data_table

get_SBC_hearings()