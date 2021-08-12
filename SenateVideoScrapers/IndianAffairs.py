import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_indian_affairs_hearings():

    url = "https://www.indian.senate.gov/hearings"
    res = requests.get(url)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('tr')
    table_rows = table_rows[1:]
    data = []
    for t in table_rows:
        row_obj = {
            "Date": t.find("span", {'class': "date-display-single"}).get_text(),
            "Time": t.findAll("span", {'class': "date-display-single"})[1].get_text(),
            "URL": "https://www.indian.senate.gov/" + t.findAll("a")[0]["href"],
            "Title": t.findAll("a")[0].get_text().replace("\n", "").rstrip().replace("\t", ""),
            "Location":  t.find("td", {'class': "views-field-field-hearing-new-office"}).get_text().rstrip().lstrip()
        }
        data.append(row_obj)
    
    for d in data:
        res_ind = requests.get(d["URL"])
        soup_ind = BeautifulSoup(res_ind.text,'html.parser')
        if soup_ind.find('div', { 'class': 'field-name-field-hearing-new-video'}) == None:
            video_url  = ""
        else:
            video_div = soup_ind.find('div', { 'class': 'field-name-field-hearing-new-video'})

            if video_div.find('iframe') == None:
                video_url = ""
            else:
                video_url =  video_div.find('iframe')["src"]
        
        d["video_url"] = video_url

    data_table = pd.DataFrame(data)
    
    return data_table

get_indian_affairs_hearings()
