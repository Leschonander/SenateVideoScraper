import pandas as pd
import os
import time

# This is the base case, that you want all files. Warning if you are 
# setting it up for the first time, it may take sometime

scripts = os.listdir("./SenateVideoScrapers")
for s in scripts:
    file_path = "./SenateVideoScrapers/" + s
    os.system(f"python3 {file_path}")
    time.sleep(1)


files = os.listdir("./SenateVideoFiles")
files = [f for f in files if f != '.DS_Store']
data_frames = []
for f in files:
    file_path = "./SenateVideoFiles/" + f
    if f != "MasterFile.csv":
        data_frame = pd.read_csv(file_path, engine='python')
    
        data_frames.append(data_frame)
    else:
        continue

data_frames = pd.concat(data_frames)
data_frames = data_frames[["Date","Time","URL","Title","Location","Committee","Date Scraped","video_url", "witnesses", "transcripts", "witness_transcripts"]]
data_frames = data_frames.rename(columns={"witnesses": "Witnesses", "transcripts": "Transcripts", "witness_transcripts": "Witness Transcripts"})
print(data_frames)
data_frames.to_csv("./SenateVideoFiles/MasterFile.csv",  encoding='utf-8', index=False)

os.system(f"python3 witnessCounts.py")
os.system(f"Rscript TagFiles.R")