import pandas as pd
import os
import time
import ast


df = pd.read_csv("./SenateVideoFiles/MasterFile.csv")
df.Witnesses = df.Witnesses.str[1:-1].str.split(',').tolist()
df.Witnesses = df.Witnesses.fillna({i: [] for i in df.index})  # replace NaN with []
df = df.explode('Witnesses')


wit_count = df.groupby(['Witnesses'])['Witnesses'].count().reset_index(name='count').sort_values(['count'], ascending=False) 
wit_count =  wit_count.reset_index().rename({'index':'id'}, axis = 'columns')
# ^ I would prefer to do a hash of the name but the names are too dirty for now so this works...
wit_count.to_csv("wit_count.csv")