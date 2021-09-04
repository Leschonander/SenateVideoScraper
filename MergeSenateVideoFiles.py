import pandas as pd
import os

# This is the base case, that you want all files. Warning if you are 
# setting it up for the first time, it may take sometime
scripts = os.listdir("./SenateVideoScrapers")
for s in scripts:
    file_path = "./SenateVideoScrapers/" + s
    os.system(f"python3 {file_path}")


files = os.listdir("./SenateVideoFiles")
data_frames = []
for f in files:
    file_path = "./SenateVideoFiles/" + f
    data_frame = pd.read_csv(file_path)
    data_frames.append(data_frame)

data_frames = pd.concat(data_frames)
data_frames.to_csv("./SenateVideoFiles/MasterFile.csv",  encoding='utf-8')
