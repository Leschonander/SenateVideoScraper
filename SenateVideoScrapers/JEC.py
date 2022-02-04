from ctypes import wintypes
import requests
import re
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
            date =  datetime.strptime(date, '%b %d %Y').strftime("%m/%d/%Y")
        
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

            if soup_ind.find_all("a", href=re.compile("files")) == None:
                d["witnesses"] = ""
            else:
                witnesses = soup_ind.find_all("a", href=re.compile("files."))
                witnesses = [w.get_text().replace("0x80", "")  for w in witnesses]
                witnesses = [
                    w.replace("Hon.", "")
                     .replace("Mr.", "")
                     .replace("Ms.", "")
                     .replace("Mrs.", "")
                     .replace("Dr.", "")
                     .replace("Ph.D.", "")
                     .replace("PhD", "")
                     .replace("Senator", "")
                     .replace("Representative", "")
                     .replace("Lt", "")
                     .replace("The Honorable", "")
                     .replace("Ranking Member", "")
                     .replace("Vice-Chair", "")
                     .replace("Vice Chairman", "")
                     .replace("Chairman", "")
                     .replace("Chairmen", "")
                     .replace("Archived Webcast", "")
                     .replace("'s Opening Statement", "")
                     .replace("'s opening Statement", "")
                     .replace("Full Hearing Transcript", "")
                     .replace("Chair", "")
                     .replace(", President", "")
                     .replace(", President and CEO", "")
                     .replace(", Senior Fellow", "")
                     .replace("Opening Statement", "")
                     .strip() 
                    for w in witnesses
                ]
                d["witnesses"] = witnesses

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