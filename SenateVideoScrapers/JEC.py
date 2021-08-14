import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_JEC_hearings():

    url = "https://www.jec.senate.gov/public/index.cfm/hearings-calendar"
    res = requests.get(url)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('article', { 'class': 'clearfix'})
    data = []
    for t in table_rows:
        
        row_obj ={
            "Date": t.find("span", {'class': "date"}).get_text().replace("\n", ""),
            "Time": "",
            "URL": t.findAll("a")[1]['href'],
            "Title": t.find('h1', {'class': 'title'}).get_text(),
            "Location": ""
        }
    
        data.append(row_obj)
    
    for d in data:
        res_ind = requests.get(d["URL"])
        soup_ind = BeautifulSoup(res_ind.text,'html.parser')
        
        if soup_ind.find('iframe') == None:
            video_url = ""
        else:
            video_url =  soup_ind.find('iframe')["src"]
        
        d["video_url"] = video_url
    
    data_table = pd.DataFrame(data)
    print(data_table)

    return data_table

get_JEC_hearings()