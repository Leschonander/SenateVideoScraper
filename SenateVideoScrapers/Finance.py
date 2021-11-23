import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime


def get_finance_hearings(rows: int):

    url = "https://www.finance.senate.gov/hearings?PageNum_rs=1&maxrows=" + str(rows)
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'https://github.com/Leschonander/SenateVideoScraper'  
    }
    res = requests.get(url, headers=headers)

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
            "Committee": "Finance",
            "Date Scraped": datetime.today().strftime("%Y-%m-%d")
        }
        
        data.append(row_obj)


    for d in data:
        if d["URL"] == "":
            video_url = ""
            d["video_url"] = video_url
        else: 
            res_ind = requests.get(d["URL"], headers=headers)
            soup_ind = BeautifulSoup(res_ind.text,'html.parser')

            if soup_ind.find('a', { 'id': 'watch-live-now'}) == None:
                video_url = ""
            else:
                video_url =  soup_ind.find('a', { 'id': 'watch-live-now'})["href"].replace("javascript:openVideoWin('", "").replace("');", "")
            
            d["video_url"] = "https://www.finance.senate.gov"  + video_url

            if soup_ind.findAll('span', {'class': 'fn'}) == None:
                d["witnesses"] = ""
            else:
                witness_html = soup_ind.findAll('span', {'class': 'fn'})
                witness_html = [w.get_text().replace("\t", "").replace("\n", "") for w in witness_html]
                # witness_html = [i for i in witness_html if "(" not in i]
                witness_html = str(witness_html)
                d["witnesses"] = witness_html

        print(d)
    data_table = pd.DataFrame(data)

    return data_table

if os.path.exists("./SenateVideoFiles/Finance.csv") == True:
    new_data = get_finance_hearings(rows=10)
    old_data = pd.read_csv("./SenateVideoFiles/Finance.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("./SenateVideoFiles/Finance.csv",  encoding='utf-8')
else: 
    get_finance_hearings(rows=999999).to_csv("./SenateVideoFiles/Finance.csv",  encoding='utf-8')

