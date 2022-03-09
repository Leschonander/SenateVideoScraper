import pdfplumber 
import pandas as pd
import requests as re
from io import BytesIO
from urllib.parse import urlparse

headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'https://github.com/Leschonander/SenateVideoScraper'  
    }

df = pd.read_csv("./SenateVideoFiles/MasterFile.csv") 
current_transcripts = pd.read_csv("New_T_File.csv")
# Explode Transcripts


df.Transcripts = df.Transcripts.str[1:-1].str.split(',').tolist()
df.Transcripts = df.Transcripts.fillna({i: [] for i in df.index})  # replace NaN with []
# df['list_of_tuples'] = list(df[['Witnesses', 'Transcripts']].to_records(index=False))

df = df.explode('Transcripts') # Transcripts

df["Transcripts"] = df["Transcripts"].str.replace("'", '').str.replace('"', '')
df = df.query('`Transcripts` != ""') # dropping blank entries...
current_transcripts_list = list(current_transcripts["url"])

not_processed = ~df.Transcripts.isin(current_transcripts_list)
df = df[not_processed]
df = df.loc[~df['Transcripts'].str.contains("https://www.indian.senate.govhttp", case=False,  na=False)]

t_length = len(df) 

seen_transcripts = {}
transcript_data = []
df = df.iloc[4000:4019] 

for i, row in enumerate(df.itertuples(index=False)):
    print(f"{i} / {t_length} => {i / t_length} | {row[9]}")
    if isinstance(row[9], str) == True:
      if ((row[9] not in seen_transcripts and ".pdf" in row[9]) or (row[9] not in seen_transcripts and "https://www.commerce.senate.gov/services/files/" in row[9])) and isinstance(row[9], str) == True:
        seen_transcripts[row[9]] = 1
        if ('https:' or 'http:' in row[9]) and "/" in row[9]:
          pdf_url = re.get(row[9], headers=headers)
          if pdf_url.status_code == 200:
                  try:
                      if pdf_url.content == b'':
                        print("Faulty PDF")
                      else:
                        pdf = pdfplumber.open(BytesIO(pdf_url.content))
                        all_text = ""
  
                        for page in pdf.pages:
                            text = page.extract_text()
                            all_text += '\n' + text
                            
                        data = {
                          "name": row[3],
                          "url": row[9],
                          "text": all_text
                        }
                        print(data)
                        transcript_data.append(data)
                  except:
                      raise
        
transcript_data_new = pd.DataFrame(transcript_data)
print(transcript_data_new)

data_frames = pd.concat([current_transcripts, transcript_data_new])
data_frames = data_frames[["name", "url", "text"]]
print(data_frames)
data_frames.to_csv("New_T_File.csv")

'''
df = df.loc[~df['Transcripts'].str.contains("https://www.indian.senate.govhttp", case=False,  na=False)]
df = df.iloc[0:]

t_length = len(df) 
# print(t_length)
seen_transcripts = {}
transcript_data = []
# Need a better way to read this to ensure faster reads later on...

faulty_pdfs = ["https://www.indian.senate.govhttps://www.indian.senate.gov/sites/default/files/SCIA%20Testimony%20Re%20S.%201364%20HR%201975%20HR%202088%20and%20HR%204881%20%28CLEARED%29%20newland.pdf"]
# ^ Bit crude but the Senate is a mess...

for i, row in enumerate(df.itertuples(index=False)):
    print(f"{i} / {t_length} => {i / t_length}")
    if isinstance(row[9], str) == True:
      if row[9] not in seen_transcripts and ".pdf" in row[9] and isinstance(row[9], str) == True and row[9] not in faulty_pdfs:
          seen_transcripts[row[9]] = 1

          if urlparse(row[9]).scheme != "":
              if "https://www.indian.senate.govhttps" in row[9]:
                pdf_url = re.get(row[9].replace("https://www.indian.senate.govhttps", "https"))
              else:
                pdf_url = re.get(row[9])
              if pdf_url.status_code == 200:
                  try:
                      if pdf_url.content == b'':
                        print("Faulty PDF")
                      else:
                        pdf = pdfplumber.open(BytesIO(pdf_url.content))
                        all_text = ""
  
                        for page in pdf.pages:
                            text = page.extract_text()
                            #print(text)
                            all_text += '\n' + text
                        data = {
                          "name": row[4],
                          "url": row[9],
                          "text": all_text
                        }
                        print(data)
                        transcript_data.append(data)
                  except:
                      raise

transcript_data = pd.DataFrame(transcript_data)

transcript_data = transcript_data[['name', 'url', 'text']]

print(transcript_data)

transcript_data.to_csv("transcript_text_part3_2.csv")
'''