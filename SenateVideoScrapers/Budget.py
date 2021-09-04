import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def get_budget_hearings(page: int):

    url = "https://www.budget.senate.gov/hearings?PageNum_rs=" + str(page)
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'https://github.com/Leschonander/SenateVideoScraper'  
    }
    res = requests.get(url, headers=headers)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('tr', { 'class': 'vevent'})
    data = []
    for t in table_rows:
        if t.find('time', {'class': 'dtstart'}) == None:
            date = ""
        else:
            date = t.find('time', {'class': 'dtstart'}).get_text()
        
        if t.find('a', {'class': 'summary'}) == None:
            url = ""
            title = ""
        else:
            url = "https://www.budget.senate.gov" + t.find('a', {'class': 'summary'})["href"]
            title = t.find('a', {'class': 'summary'}).get_text().replace("\n", "").replace("\t", "")

        if t.find('span', {'class': 'location'}) == None:
            location = ""
        else:
            location =  t.find('span', {'class': 'location'}).get_text()
        
        row_obj = {
            "Date": date,
            "Time": "",
            "URL": url,
            "Title": title,
            "Location": location,
            "Committee": "Budget"
        }
        
        data.append(row_obj)
    
    for d in data:
        if d["URL"] == "":
            d["video_url"] = ""
        else:
            res_ind = requests.get(d["URL"])
            soup_ind = BeautifulSoup(res_ind.text,'html.parser')

            if soup_ind.find('a', { 'id': 'watch-live-now'}) == None:
                video_url = ""
            else:
                video_url =  "https://www.budget.senate.gov" + soup_ind.find('a', { 'id': 'watch-live-now'})["href"].replace("javascript:openVideoWin('", "").replace("');", "")
            
            d["video_url"] = video_url
    
    data_table = pd.DataFrame(data)
    print(data_table)

    return data_table

if os.path.exists("../SenateVideoFiles/Budget.csv") == True:
    new_data = get_budget_hearings(page = 1)
    old_data = pd.read_csv("../SenateVideoFiles/Budget.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("../SenateVideoFiles/Budget.csv")
else: 

    pages = [i for i in range(1, 15)]
    data_table_list = []
    for p in pages:
        result = get_budget_hearings(p)
        print(result)
        data_table_list.append(result)

    data_table_list_master = pd.concat(data_table_list)
    data_table_list_master.to_csv("../SenateVideoFiles/Budget.csv")
