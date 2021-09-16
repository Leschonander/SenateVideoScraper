import pandas as pd
import argparse
import os
import time


parser = argparse.ArgumentParser(description='Extract data from the Senate Committee websites')

parser.add_argument('Command',
                       metavar='command',
                       type=str,
                       help='the specific way to extract the data')

args = parser.parse_args()

command = args.Command
scripts = os.listdir("./SenateVideoScrapers")
scripts = [s.replace(".py", '') for s in scripts]

if(command == 'extract-all'):
    scripts = os.listdir("./SenateVideoScrapers")
    for s in scripts:
        file_path = "./SenateVideoScrapers/" + s
        os.system(f"python3 {file_path}")
        time.sleep(1)


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

for s in scripts:
    if(command == f'extract-all-{s}'):
        file_path = "./SenateVideoScrapers/" + s + ".py"
        os.system(f"python3 {file_path}")