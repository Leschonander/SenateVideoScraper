import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_finance_hearings():

    url = "https://www.finance.senate.gov/hearings?PageNum_rs=1&maxrows=999999"
    res = requests.get(url)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('tr', { 'class': 'vevent'})
    data = []
    for t in table_rows:
        if  t.find("td", {'class': "hearing-td"}) == None:
            link = ""
            title = ""
        else:
            link = "https://www.finance.senate.gov" + t.find("td", {'class': "hearing-td"}).find("a")["href"]
            title = t.find("td", {'class': "hearing-td"}).find("a").get_text().replace("\n", "").rstrip().replace("\t", "")
        
        if  t.find("time") == None:
            date = ""
        else:
            date = t.find("time").get_text()

        row_obj ={
            "Date": date,
            "Time": "",
            "URL": link,
            "Title": title,
            "Location": "",
            "Committee": "Finance"
        }
        
        data.append(row_obj)


    for d in data:
        if d["URL"] == "":
            video_url = ""
            d["video_url"] = video_url
        else: 
            res_ind = requests.get(d["URL"])
            soup_ind = BeautifulSoup(res_ind.text,'html.parser')

            if soup_ind.find('a', { 'id': 'watch-live-now'}) == None:
                video_url = ""
            else:
                video_url =  soup_ind.find('a', { 'id': 'watch-live-now'})["href"].replace("javascript:openVideoWin('", "").replace("');", "")
            
            d["video_url"] = "https://www.finance.senate.gov"  + video_url
        print(d)
    data_table = pd.DataFrame(data)

    return data_table
        
get_finance_hearings().to_csv("../SenateVideoFiles/Finance.csv")