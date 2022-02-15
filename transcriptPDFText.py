import pdfplumber 
import pandas as pd
import requests as re
from io import BytesIO


df = pd.read_csv("./SenateVideoFiles/JEC.csv") # SenateVideoFiles/MasterFile


# Explode Transcripts


df.transcripts = df.transcripts.str[1:-1].str.split(',').tolist()
df.transcripts = df.transcripts.fillna({i: [] for i in df.index})  # replace NaN with []
df['list_of_tuples'] = list(df[['witnesses', 'transcripts']].to_records(index=False))

df = df.explode('transcripts') # Transcripts

df["transcripts"] = df["transcripts"].str.replace("'", '')


seen_transcripts = {}
transcript_data = []

for i, row in enumerate(df.itertuples(index=False)):
    if row[10] not in seen_transcripts and ".pdf" in row[10]:
        seen_transcripts[row[10]] = 1
        pdf_url = re.get(row[10])
        try:
            pdf = pdfplumber.open(BytesIO(pdf_url.content))
            all_text = ""

            for page in pdf.pages:
                text = page.extract_text()
                #print(text)
                all_text += '\n' + text
            data = {
                "name": row[4],
                "url": row[10],
                "text": all_text
            }
            print(data)
            transcript_data.append(data)
        except:
            raise

transcript_data = pd.DataFrame(transcript_data)
print(transcript_data)

transcript_data.to_csv("transcript_text.csv")
