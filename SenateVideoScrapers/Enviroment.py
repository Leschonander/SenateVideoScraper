import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime
import re

def get_enviroment_hearings(page: int):

    url = "https://www.epw.senate.gov/public/index.cfm/hearings?page=" + str(page)
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'https://github.com/Leschonander/SenateVideoScraper'  
    }
    res = requests.get(url, headers=headers)

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
                "Committee": "Enviroment",
                "Date Scraped": datetime.today().strftime("%Y-%m-%d")
            }

            data.append(row_obj)
    
    for d in data:
        if d["URL"] == "":
            video_url = ""
        else:
            res_ind = requests.get(d["URL"], headers=headers)
            soup_ind = BeautifulSoup(res_ind.text,'html.parser')

            if soup_ind.find('iframe', { 'class': 'embed-responsive-item'}) == None:
                video_url = ""
            else:
                video_url =  soup_ind.find('iframe', { 'class': 'embed-responsive-item'})["src"]
            
            if soup_ind.findAll('li', {'class': 'list-group-item'}) == None:
                d["witnesses"] = ""
                d["transcripts"] = ""
                d["witness_transcripts"] = ""
            else:
                witness_cards = soup_ind.findAll('li', {'class': 'list-group-item'})
                witness = []
                transcripts = []
                witness_transcripts = []

                for w in witness_cards:

                    if w.find('div',  {'class': 'person'}) == None:
                        witness_name = ''
                    else: 
                        witness_name = w.find('div',  {'class': 'person'}).get_text().replace("\t", "").replace("\n", " ").replace("0x80", "").strip()
                        witness_name = witness_name.replace("Hon.", "").replace("Mr.", "").replace("Ms.", "").replace("Mrs.", "").replace("Dr.", "").replace("Ph.D.", "").replace("PhD", "").replace("Senator", "").replace("Representative", "").replace("Lt", "").replace("The Honorable", "").replace("(R-GA)", "").strip() 
                        witness_name = ' '.join(witness_name.split())
                    
                    if w.find('a', string=re.compile(r'Testimony')) == None:
                        witness_url = ''
                    else:
                        testimony = w.find('a', string=re.compile(r'Testimony'))
                        link_to_pdf = "https://www.epw.senate.gov" + testimony["href"] 

                        try:
                            pdf_page = requests.get(link_to_pdf, headers=headers)
                            witness_url = pdf_page.url
                        except:
                            witness_url = ''

                    witness.append(witness_name)
                    transcripts.append(witness_url)
                    witness_transcripts.append((witness_name,witness_url))

                d["witnesses"] = witness
                d["transcripts"] = transcripts
                d["witness_transcripts"] = witness_transcripts

          
        d["video_url"] = video_url
        print(d)
    
    data_table = pd.DataFrame(data)

    return data_table

if os.path.exists("./SenateVideoFiles/Enviroment.csv") == True:
    pages = [i for i in range(1, 2)]
    data_table_list = []
    for p in pages:
        result = get_enviroment_hearings(p)
        print(result, p)
        data_table_list.append(result)
    new_data = pd.concat(data_table_list)

    old_data = pd.read_csv("./SenateVideoFiles/Enviroment.csv")
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("./SenateVideoFiles/Enviroment.csv",  encoding='utf-8')

else: 
    pages = [i for i in range(1, 71)]
    data_table_list = []
    for p in pages:
        result = get_enviroment_hearings(p)
        print(result, p)
        data_table_list.append(result)

    data_table_list_master = pd.concat(data_table_list)
    data_table_list_master.to_csv("./SenateVideoFiles/Enviroment.csv",  encoding='utf-8')
