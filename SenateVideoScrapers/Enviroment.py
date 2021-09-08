import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime


def get_enviroment_hearings(page: int):

    url = "https://www.epw.senate.gov/public/index.cfm/hearings?page=" + str(page)
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'https://github.com/Leschonander/SenateVideoScraper'  
    }
    res = requests.get(url, headers=headers)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('tr')
    data = []
    for t in table_rows:
        
        if t.findAll("td") == []:
            continue
        else:
            if  t.find("td", {'class': 'recordListDate'}) == None:
                date = ""
            else:
                date = t.find("td", {'class': 'recordListDate'}).get_text()

            if  t.find("td", {'class': 'recordListTime'}) == None:
                time = ""
            else:
                time = t.find("td", {'class': 'recordListTime'}).get_text()
            
            if t.find("a")["href"] == None:
                url = ""
                title = ""
            else:
                url = "https://www.epw.senate.gov" + t.find("a")["href"]
                title = t.find("a").get_text()

            row_obj = {
                "Date": date,
                "Time": time,
                "URL": url,
                "Title": title,
                "Location": "",
                "Committee": "Enviroment",
                "Date Scraped": datetime.today().strftime("%Y-%m-%d")
            }

            data.append(row_obj)
    
    for d in data:
        if d["URL"] == "":
            video_url = ""
        else:
            res_ind = requests.get(d["URL"], headers=headers)
            soup_ind = BeautifulSoup(res_ind.text,'html.parser')

            if soup_ind.find('iframe', { 'class': 'embed-responsive-item'}) == None:
                video_url = ""
            else:
                video_url =  soup_ind.find('iframe', { 'class': 'embed-responsive-item'})["src"]
        
        d["video_url"] = video_url
    
    data_table = pd.DataFrame(data)

    return data_table

if os.path.exists("./SenateVideoFiles/Enviroment.csv") == True:
    pages = [i for i in range(1, 2)]
    data_table_list = []
    for p in pages:
        result = get_enviroment_hearings(p)
        print(result, p)
        data_table_list.append(result)
    new_data = pd.concat(data_table_list)

    old_data = pd.read_csv("./SenateVideoFiles/Enviroment.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("./SenateVideoFiles/Enviroment.csv",  encoding='utf-8')

else: 
    pages = [i for i in range(1, 71)]
    data_table_list = []
    for p in pages:
        result = get_enviroment_hearings(p)
        print(result, p)
        data_table_list.append(result)

    data_table_list_master = pd.concat(data_table_list)
    data_table_list_master.to_csv("./SenateVideoFiles/Enviroment.csv",  encoding='utf-8')
