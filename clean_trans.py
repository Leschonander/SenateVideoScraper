import pandas as pd

tests = pd.read_csv("transcript_text.csv")
tests = tests[["name", "url", "text"]]

df = pd.read_csv("./SenateVideoFiles/MasterFile.csv") 

# Explode Transcripts


df.Transcripts = df.Transcripts.str[1:-1].str.split(',').tolist()
df.Transcripts = df.Transcripts.fillna({i: [] for i in df.index})  # replace NaN with []
# df['list_of_tuples'] = list(df[['Witnesses', 'Transcripts']].to_records(index=False))

df = df.explode('Transcripts') # Transcripts

df["Transcripts"] = df["Transcripts"].str.replace("'", '')
df = df.query('`Transcripts` != ""') # dropping blank entries...

df = df.loc[~df['Transcripts'].str.contains("https://www.indian.senate.govhttp", case=False,  na=False)]

df = df[["Transcripts", "Title"]]
df = df.rename(columns={"Transcripts": "url"})
result = pd.merge(tests, df, on=["url"])
result = result[["Title", "url", "text"]]
df = df.rename(columns={"Title": "name"})
result.to_csv("New_T_File.csv")
