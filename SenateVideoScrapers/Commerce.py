import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_commerce_hearings(year: int):

    url = "https://www.commerce.senate.gov/hearings?month=&year=" + str(year)
    res = requests.get(url)
    print(url)
    soup =  BeautifulSoup(res.text,'html.parser')
    
    table_rows = soup.findAll('div', { 'class': 'element'})
    data = []
    for t in table_rows:

        if t.find("span", {'class': "element-datetime"}) == None:
            date = ""
        else:
            date = t.find("span", {'class': "element-datetime"}).get_text()
        
        if t.findAll("a")[0] == None:
            url = ""
        else:
            url = t.findAll("a")[0]["href"]
        
        if t.find("div", {'class': "element-title"}) == None:
            title = ""
        else:
            title = t.find("div", {'class': "element-title"}).get_text().replace("\n", "").replace("\t", "").strip()

        row_obj ={
            "Date": date,
            "Time": "",
            "URL": url,
            "Title": title,
            "Location": "",
            "Committee": "Commerce"
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
        print(d)
    data_table = pd.DataFrame(data)
    
    return data_table

years = [i for i in range(2003, 2022)]

data_table_list = []
for y in years:
    result = get_commerce_hearings(y)
    print(result, y)
    data_table_list.append(result)

data_table_list_master = pd.concat(data_table_list)
data_table_list_master.to_csv("../SenateVideoFiles/Commerce.csv")
