import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_JEC_hearings(year: int):

    url = "https://www.jec.senate.gov/public/index.cfm/hearings-calendar?YearDisplay=" + str(year)
    res = requests.get(url)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('article', { 'class': 'clearfix'})
    data = []
    for t in table_rows:

        if t.find('h1', {'class': 'title'}) == None:
            title = ""
            url = ""
        else:
            title = t.find('h1', {'class': 'title'}).get_text()
        
        if  t.find("span", {'class': "date"}) == None:
            date = ""
            url = t.find('h1', {'class': 'title'}).find('a')['href']
        else:
            date = t.find("span", {'class': "date"}).get_text().replace("\n", "")
        
        row_obj ={
            "Date": date,
            "Time": "",
            "URL": url,
            "Title":title,
            "Location": "",
            "Committee": "JEC"
        }
        
        data.append(row_obj)
    
    for d in data:
        if d["URL"] == "":
             d["video_url"] = ""
        else:
            res_ind = requests.get(d["URL"])
            soup_ind = BeautifulSoup(res_ind.text,'html.parser')
            
            if soup_ind.find('iframe') == None:
                video_url = ""
            else:
                video_url =  soup_ind.find('iframe')["src"]
            
            d["video_url"] = video_url
        print(d)
    data_table = pd.DataFrame(data)

    return data_table

#get_JEC_hearings()
years = [i for i in range(2007, 2022)]
data_table_list = []
for y in years:
    result = get_JEC_hearings(y)
    print(result, y)
    data_table_list.append(result)

data_table_list_master = pd.concat(data_table_list)
data_table_list_master.to_csv("../SenateVideoFiles/JEC.csv")