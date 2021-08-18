import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_armed_hearings():

    url = "https://www.armed-services.senate.gov/hearings?c=all&maxrows=5000"
    res = requests.get(url)

    soup =  BeautifulSoup(res.text,'html.parser')

    table_rows = soup.findAll('tr', { 'class': 'vevent'})
    data = []
    for t in table_rows:
        if t.find("time").get_text() == None:
            date = ["", ""]
        else:
            date = t.find("time").get_text().split(" ")
        
        if  t.find("a") == None:
            url = ""
            title = ""
        else:
            url = t.find("a")["href"].replace("\n", "").replace("\t", "")
            title = t.find("a").get_text().replace("\n", "").replace("\t", "").rstrip()

        if  t.find("span", {'class': "location"}) == None:
            location = ""
        else:
            location =  t.find("span", {'class': "location"}).get_text().rstrip().lstrip()
        
        

        row_obj = {
            "Date": date[0],
            "Time": date[1],
            "URL": url,
            "Title": title,
            "Location": location,
            "Committee": "Armed"
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
                video_url =  soup_ind.find('a', { 'id': 'watch-live-now'})["href"].replace("javascript:openVideoWin('", "").replace("');", "")

            d["video_url"] = video_url
        print(d)
    data_table = pd.DataFrame(data)
    print(data_table)
    
    return data_table

get_armed_hearings().to_csv("../SenateVideoFiles/Armed.csv")