import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime

def get_energy_hearings(page: int):

    url = "https://www.energy.senate.gov/hearings?page=" + str(page)
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'https://github.com/Leschonander/SenateVideoScraper'  
    }
    res = requests.get(url, headers=headers)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('div', { 'class': 'element'})
    data = []
    for t in table_rows:

        if t.find('span', {'class': 'element-date'}) == None:
            date = ""
        else:
            date = t.find('span', {'class': 'element-date'}).get_text()
        
        if t.find('span', {'class': 'element-time'}) == None:
            time = ""
        else:
            time = t.find('span', {'class': 'element-time'}).get_text()

        if t.find('a') == None:
            url = ""
        else:
            url = t.find('a')["href"]
        
        if t.find('div', {'class': 'element-title'}) == None:
            title = ""
        else:
            title = t.find('div', {'class': 'element-title'}).get_text().strip()
        

        row_obj = {
            "Date": date,
            "Time": time,
            "URL": url,
            "Title": title,
            "Location": "",
            "Committee": "Energy",
            "Date Scraped": datetime.today().strftime("%Y-%m-%d")
        }

        data.append(row_obj)
    
    for d in data:
        if d["URL"] == "":
            d["video_url"] = ""
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

if os.path.exists("./SenateVideoFiles/Energy.csv") == True:
    new_data = get_energy_hearings(page = 1)
    old_data = pd.read_csv("./SenateVideoFiles/Energy.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("./SenateVideoFiles/Energy.csv")

else:
    pages = [i for i in range(1, 17)]
    data_table_list = []
    for p in pages:
        result = get_energy_hearings(p)
        print(result)
        data_table_list.append(result)

    data_table_list_master = pd.concat(data_table_list)
    data_table_list_master.to_csv("./SenateVideoFiles/Energy.csv")
