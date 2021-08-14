import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_commerce_hearings():

    url = "https://www.commerce.senate.gov/hearings"
    res = requests.get(url)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('div', { 'class': 'element'})
    data = []
    for t in table_rows:
        row_obj ={
            "Date": t.find("span", {'class': "element-datetime"}).get_text(),
            "Time": "",
            "URL": t.findAll("a")[0]["href"],
            "Title": t.find("div", {'class': "element-title"}).get_text(),
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

get_commerce_hearings()