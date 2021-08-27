import pandas as pd
import os


files = os.listdir("./SenateVideoFiles")
data_frames = []
for f in files:
    file_path = "./SenateVideoFiles/" + f
    data_frame = pd.read_csv(file_path)
    data_frames.append(data_frame)

data_frames = pd.concat(data_frames)
data_frames.to_csv("./SenateVideoFiles/MasterFile.csv",  encoding='utf-8')