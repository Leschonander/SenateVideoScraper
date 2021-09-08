import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime


def get_indian_affairs_hearings(page: int):

    url = "https://www.indian.senate.gov/hearings?page=" + str(page)
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'https://github.com/Leschonander/SenateVideoScraper'  
    }
    res = requests.get(url, headers=headers)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('tr')
    table_rows = table_rows[1:]
    data = []
    for t in table_rows:

        if  t.find("td", {'class': "views-field-field-hearing-new-office"}) == None:
            location = ""
        else:
            location = t.find("td", {'class': "views-field-field-hearing-new-office"}).get_text().rstrip().lstrip()

        row_obj = {
            "Date": t.find("span", {'class': "date-display-single"}).get_text(),
            "Time": t.findAll("span", {'class': "date-display-single"})[1].get_text(),
            "URL": "https://www.indian.senate.gov/" + t.findAll("a")[0]["href"],
            "Title": t.findAll("a")[0].get_text().replace("\n", "").rstrip().replace("\t", ""),
            "Location": location,
            "Committee": "Indian Affairs",
            "Date Scraped": datetime.today().strftime("%Y-%m-%d")
        }
        data.append(row_obj)
    
    for d in data:
        res_ind = requests.get(d["URL"], headers=headers)
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

if os.path.exists("./SenateVideoFiles/IndianAffairs.csv") == True:
    pages = [i for i in range(1, 2)]
    data_table_list = []
    for p in pages:
        result = get_indian_affairs_hearings(p)
        print(result, p)
        data_table_list.append(result)
    new_data = pd.concat(data_table_list)

    old_data = pd.read_csv("./SenateVideoFiles/IndianAffairs.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("./SenateVideoFiles/IndianAffairs.csv",  encoding='utf-8')

else:
    pages = [i for i in range(0, 49)]
    data_table_list = []
    for p in pages:
        result = get_indian_affairs_hearings(p)
        print(result, p)
        data_table_list.append(result)

    data_table_list_master = pd.concat(data_table_list)
    data_table_list_master.to_csv("./SenateVideoFiles/IndianAffairs.csv",  encoding='utf-8')
