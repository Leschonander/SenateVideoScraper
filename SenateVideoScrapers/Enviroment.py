import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_enviroment_hearings(page: int):

    url = "https://www.epw.senate.gov/public/index.cfm/hearings?page=" + str(page)
    res = requests.get(url)

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
                "Committee": "Enviroment"
            }

            data.append(row_obj)
    
    for d in data:
        if d["URL"] == "":
            video_url = ""
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

pages = [i for i in range(1, 23)]
data_table_list = []
for p in pages:
    result = get_enviroment_hearings(p)
    print(result)
    data_table_list.append(result)

data_table_list_master = pd.concat(data_table_list)
data_table_list_master.to_csv("../SenateVideoFiles/Enviroment.csv")
