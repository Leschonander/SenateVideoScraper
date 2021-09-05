import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime

def get_JEC_hearings(year: int):

    url = "https://www.jec.senate.gov/public/index.cfm/hearings-calendar?YearDisplay=" + str(year)
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'https://github.com/Leschonander/SenateVideoScraper'  
    }
    res = requests.get(url, headers=headers)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('article', { 'class': 'clearfix'})
    data = []
    for t in table_rows:

        if t.find('h1', {'class': 'title'}) == None:
            title = ""
            url = ""
        else:
            title = t.find('h1', {'class': 'title'}).get_text()
            url = t.find('h1', {'class': 'title'}).find('a')['href']

        
        if t.find("span", {'class': "date"}) == None:
            date = ""
        else:
            date = t.find("span", {'class': "date"}).get_text().replace("\n", "")
        
        row_obj ={
            "Date": date,
            "Time": "",
            "URL": url,
            "Title":title,
            "Location": "",
            "Committee": "JEC",
            "Date Scraped": datetime.today().strftime("%Y-%m-%d")
        }
        
        data.append(row_obj)
    
    for d in data:
        if d["URL"] == "":
             d["video_url"] = ""
        else:

            res_ind = requests.get(d["URL"], headers=headers)
            soup_ind = BeautifulSoup(res_ind.text,'html.parser')
            
            if soup_ind.find('iframe') == None:
                video_url = ""
            else:
                video_url =  soup_ind.find('iframe')["src"]
            
            d["video_url"] = video_url
        print(d)
    data_table = pd.DataFrame(data)

    return data_table

if os.path.exists("./SenateVideoFiles/JEC.csv") == True:
    current_year =  datetime.today().year
    years = [i for i in range(current_year, current_year + 1)]
    data_table_list = []
    for p in years:
        result = get_JEC_hearings(p)
        print(result, p)
        data_table_list.append(result)
    new_data = pd.concat(data_table_list)

    old_data = pd.read_csv("./SenateVideoFiles/JEC.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("./SenateVideoFiles/JEC.csv",  encoding='utf-8')

else:
    current_year =  datetime.today().year
    years = [i for i in range(2007, current_year + 1)]
    data_table_list = []
    for y in years:
        result = get_JEC_hearings(y)
        print(result)
        data_table_list.append(result)

    data_table_list_master = pd.concat(data_table_list)
    data_table_list_master.to_csv("./SenateVideoFiles/JEC.csv",  encoding='utf-8')