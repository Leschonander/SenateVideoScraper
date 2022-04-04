import requests
from bs4 import BeautifulSoup
import pandas as pd
import os 
from datetime import datetime

def get_homeland_security_hearings(page: int):

    url = f"https://www.hsgac.senate.gov/hearings?PageNum_rs={page}&c=all"
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'https://github.com/Leschonander/SenateVideoScraper'  
    }
    res = requests.get(url, headers=headers)
    
    soup =  BeautifulSoup(res.text,'html.parser')
    
    table_rows = soup.findAll('tr', { 'class': 'vevent'})
    data = []
    for t in table_rows:
        if t.find('time', {'class': 'dtstart'}) == None:
            date = ""
            time = ""
        else:
            date_time = t.find('time', {'class': 'dtstart'}).get_text().split(" ")
            date =  date_time[0]
            time = date_time[1]
        
        if t.find('a', {'class': 'summary'}) == None:
            url = ""
            title = ""
        else:
            url = t.find('a', {'class': 'summary'})["href"]
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
            "Committee": "Homeland Security",
            "Date Scraped": datetime.today().strftime("%Y-%m-%d")
        }
        data.append(row_obj)
    
    for d in data:
        if d["URL"] == "":
            video_url = ""
        else:
            res_ind = requests.get(d["URL"], headers=headers)
            soup_ind = BeautifulSoup(res_ind.text,'html.parser')

            if soup_ind.find('a', { 'id': 'watch-live-now'}) == None:
                video_url = ""
            else:
                video_url =  soup_ind.find('a', { 'id': 'watch-live-now'})["href"].replace("javascript:openVideoWin('", "").replace("');", "")

            if soup_ind.findAll('ul', {'class': 'people'}) == None or soup_ind.findAll('ul', {'class': 'people'}) == []:
                d["witnesses"] = ""
                d["transcripts"] = ""
                d["witness_transcripts"] = ""

            else:
                people_list = soup_ind.find("ul", {"class": "people"})

                witness_cards = people_list.findAll("li")
                witness = []
                transcripts = []
                witness_transcripts = []

                for w in witness_cards:

                    if  w.find('span',  {'class': 'fn'}) == None:
                        witness_name = ''
                    else: 
                        witness_name = w.find('span',  {'class': 'fn'}).get_text().replace("\t", "").replace("\n", " ").replace("0x80", "").strip()
                        witness_name = witness_name.replace("Hon.", "").replace("Mr.", "").replace("Ms.", "").replace("Mrs.", "").replace("Dr.", "").replace("Ph.D.", "").replace("PhD", "").replace("Senator", "").replace("Representative", "").replace("Lt", "").replace("The Honorable", "").replace("(R-GA)", "").strip() 
                        witness_name = ' '.join(witness_name.split())

                    

                    if w.find('a',  {'class': 'hearing-pdf'}) == None:
                        witness_url = ''
                    else:
                        testimony = w.find('a',  {'class': 'hearing-pdf'})
                        if 'https:' in testimony["href"] or 'http:' in testimony["href"]:
                            try:
                                pdf_page = requests.get(testimony["href"], headers=headers)
                                witness_url = pdf_page.url
                            except:
                                witness_url = ''
                            
                    
                    witness.append(witness_name)
                    transcripts.append(witness_url)
                    witness_transcripts.append((witness_name,witness_url))

                d["witnesses"] = witness
                d["transcripts"] = transcripts
                d["witness_transcripts"] = witness_transcripts
            '''
            if soup_ind.findAll('span', {'class': 'fn'}) == None:
                d["witnesses"] = ""
            else:
                witness_html = soup_ind.findAll('span', {'class': 'fn'})
                witness_html = [w.get_text().replace("\t", "").replace("\n", " ").replace("0x80", "")  for w in witness_html]
                witness_html = [i for i in witness_html if "(" not in i]
                witness_html = [
                    w.replace("Hon.", "")
                     .replace("Mr.", "")
                     .replace("Ms.", "")
                     .replace("Mrs.", "")
                     .replace("Dr.", "")
                     .replace("Ph.D.", "")
                     .replace("PhD", "")
                     .replace("Senator", "")
                     .replace("Representative", "")
                     .replace("Lt", "")
                     .replace("The Honorable", "")
                     .replace(", PH.D.", "")
                     .replace(", D.PHIL.", "")
                     .strip() 
                    for w in witness_html
                ]
                witness_html = [' '.join(w.split()) for w in witness_html]
                witness_html = list(set(witness_html))
                d["witnesses"] = witness_html

                transcripts = []
                for a in soup_ind.find_all('a', href=True): 
                    if "Download Testimony" in a.text:
                        res_tran = requests.get(a['href'], headers=headers)
                        transcripts.append(res_tran.url)
                d["transcripts"] = transcripts
                '''
        d["video_url"] = video_url
        print(d)

    data_table = pd.DataFrame(data)

    return data_table
        
if os.path.exists("./SenateVideoFiles/HomeLandSecurity.csv") == True:
    pages = [i for i in range(1, 2)]
    data_table_list = []
    for p in pages:
        result = get_homeland_security_hearings(p)
        print(result, p)
        data_table_list.append(result)
    new_data = pd.concat(data_table_list)

    old_data = pd.read_csv("./SenateVideoFiles/HomeLandSecurity.csv",  lineterminator='\n')
    combined_data = pd.concat([new_data, old_data])
    combined_data = combined_data.drop_duplicates("URL")
    combined_data.to_csv("./SenateVideoFiles/HomeLandSecurity.csv",  encoding='utf-8')

else: 
    pages = [i for i in range(1, 96)]
    data_table_list = []
    for p in pages:
        result = get_homeland_security_hearings(p)
        print(result, p)
        data_table_list.append(result)

    data_table_list_master = pd.concat(data_table_list)
    data_table_list_master.to_csv("./SenateVideoFiles/HomeLandSecurity.csv",  encoding='utf-8')
