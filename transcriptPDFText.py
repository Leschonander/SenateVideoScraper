import pdfplumber 
import pandas as pd
import requests as re
from io import BytesIO
from urllib.parse import urlparse


df = pd.read_csv("./SenateVideoFiles/MasterFile.csv") 

# Explode Transcripts


df.Transcripts = df.Transcripts.str[1:-1].str.split(',').tolist()
df.Transcripts = df.Transcripts.fillna({i: [] for i in df.index})  # replace NaN with []
# df['list_of_tuples'] = list(df[['Witnesses', 'Transcripts']].to_records(index=False))

df = df.explode('Transcripts') # Transcripts

df["Transcripts"] = df["Transcripts"].str.replace("'", '')
t_length = len(df)
seen_transcripts = {}
transcript_data = []
# Need a better way to read this to ensure faster reads later on...
for i, row in enumerate(df.itertuples(index=False)):
    print(f"{i} / {t_length} => {i / t_length}")
    if row[9] not in seen_transcripts and ".pdf" in row[9]:
        seen_transcripts[row[9]] = 1
        if urlparse(row[9]).scheme != "":
            pdf_url = re.get(row[9])
            if pdf_url.status_code == 200:
                try:
                    
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
print(transcript_data)

transcript_data.to_csv("transcript_text.csv")
