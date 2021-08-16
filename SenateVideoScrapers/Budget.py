import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_budget_hearings(page):

    url = "https://www.budget.senate.gov/hearings?PageNum_rs=" + str(page)
    res = requests.get(url)

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

pages = [i for i in range(1, 15)]
data_table_list = []
for p in pages:
    result = get_budget_hearings(p)
    print(result)
    data_table_list.append(result)

data_table_list_master = pd.concat(data_table_list)
data_table_list_master.to_csv("../SenateVideoFiles/Budget.csv")
