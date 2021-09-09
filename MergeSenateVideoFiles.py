import pandas as pd
import os

# This is the base case, that you want all files. Warning if you are 
# setting it up for the first time, it may take sometime

scripts = os.listdir("./SenateVideoScrapers")
for s in scripts:
    file_path = "./SenateVideoScrapers/" + s
    os.system(f"python3 {file_path}")

'
files = os.listdir("./SenateVideoFiles")
data_frames = []
for f in files:
    file_path = "./SenateVideoFiles/" + f
    if f != "MasterFile.csv":
        data_frame = pd.read_csv(file_path, engine='python')
    
        data_frames.append(data_frame)
    else:
        continue

data_frames = pd.concat(data_frames)
data_frames = data_frames[["Date","Time","URL","Title","Location","Committee","Date Scraped","video_url"]]
print(data_frames)
data_frames.to_csv("./SenateVideoFiles/MasterFile.csv",  encoding='utf-8', index=False)
