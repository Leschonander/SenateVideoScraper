import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_foreign_hearings():

    url = "https://www.foreign.senate.gov/hearings?maxrows=5000"
    res = requests.get(url)

    soup =  BeautifulSoup(res.text,'html.parser')
    table_rows = soup.findAll('tr', { 'class': 'vevent'})
    data = []
    for t in table_rows:
        if t.find('time', {'class': 'dtstart'}) == None:
            date = ""
            time = ""
        else:
            date_time = t.find('time', {'class': 'dtstart'}).get_text().split(" ")
            
            try:
                date = date_time[0]
            except:
                date = ""
            try:
                time = date_time[1]
            except IndexError:
                time = ""
        
        if t.find('a', {'class': 'summary'}) == None:
            url = ""
            title = ""
        else:
            url = "https://www.foreign.senate.gov" + t.find('a', {'class': 'summary'})["href"]
            title = t.find('a', {'class': 'summary'}).get_text().replace("\n", "").replace("\t", "")
        

        if t.find('span', {'class': 'location'}) == None:
            location = ""
        else:
            location =  t.find('span', {'class': 'location'}).get_text()
            
        row_obj = {
            "Date": date,
            "Time": time,
            "URL": url,
            "Title": title,
            "Location": location,
            "Committee": "Foreign"
        }
        
        data.append(row_obj)
    
    for d in data:
        res_ind = requests.get(d["URL"])
        soup_ind = BeautifulSoup(res_ind.text,'html.parser')
        
        if soup_ind.find('iframe', { 'class': 'streaminghearing'}) == None:
            video_url = ""
        else:
            video_url =  soup_ind.find('iframe', { 'class': 'streaminghearing'})["src"]
        
        d["video_url"] = video_url
    
    data_table = pd.DataFrame(data)
    
    return data_table


get_foreign_hearings()