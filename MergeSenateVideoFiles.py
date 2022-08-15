import pandas as pd
import os
from dotenv import load_dotenv
import time
import logging
import sentry_sdk
from sentry_sdk import capture_message
from sentry_sdk.integrations.logging import LoggingIntegration

load_dotenv()

sentry_logging = LoggingIntegration(
    level=logging.DEBUG,       
    event_level=logging.DEBUG  
)
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[
        sentry_logging,
    ],
    traces_sample_rate=1.0,
)


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

master_file = pd.read_csv("./SenateVideoFiles/MasterFile.csv")
master_file.reset_index(inplace=True)

tag_file = pd.read_csv("MasterFileWithTags.csv")
tag_file.reset_index(inplace=True)
tag_file = tag_file[["index", "Tags"]]
merged_data = pd.merge(master_file, tag_file, on =  "index", how="left")
merged_data.to_csv("./SenateVideoFiles/MasterFile.csv",  encoding='utf-8', index=False)


logging.info("Scraper run complete")
