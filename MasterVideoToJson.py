import pandas as pd
import json

dataframe = pd.read_csv("./SenateVideoFiles/MasterFile.csv")
records = dataframe.to_dict("records")
with open('MasterFile.json', 'w') as outfile:
    json.dump(records, outfile)