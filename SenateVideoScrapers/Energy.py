import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_energy_hearings(page: int):

    url = "https://www.energy.senate.gov/hearings?page=" + str(page)
    res = requests.get(url)

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
            "Committee": "Energy"
        }

        data.append(row_obj)
    
    for d in data:
        if d["URL"] == "":
            d["video_url"] = ""
        else:
            res_ind = requests.get(d["URL"])
            soup_ind = BeautifulSoup(res_ind.text,'html.parser')
            
            if soup_ind.find('iframe', { 'class': 'embed-responsive-item'}) == None:
                video_url = ""
            else:
                video_url =  soup_ind.find('iframe', { 'class': 'embed-responsive-item'})["src"]
        
            d["video_url"] = video_url
    
    data_table = pd.DataFrame(data)

    return data_table

pages = [i for i in range(1, 17)]
data_table_list = []
for p in pages:
    result = get_energy_hearings(p)
    print(result)
    data_table_list.append(result)

data_table_list_master = pd.concat(data_table_list)
data_table_list_master.to_csv("../SenateVideoFiles/Energy.csv")