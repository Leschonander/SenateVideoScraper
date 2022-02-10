import pandas as pd
import os
import time
import ast


df = pd.read_csv("./SenateVideoFiles/MasterFile.csv")
df.Witnesses = df.Witnesses.str[1:-1].str.split(',').tolist()
df.Witnesses = df.Witnesses.fillna({i: [] for i in df.index})  # replace NaN with []
df = df.explode('Witnesses')

df["Witnesses"] = df["Witnesses"].str.title()
df["Witnesses"] = df["Witnesses"].str.replace("'", '')
df["Witnesses"] = df["Witnesses"].str.replace("Honorable", '')
df["Witnesses"] = df["Witnesses"].str.strip()


wit_count = df.groupby(['Witnesses'])['Witnesses'].count()

# wit_count = wit_count.query('`Witnesses` != ""') 


wit_count = wit_count.reset_index(name='count').sort_values(['count'], ascending=False) 
wit_count =  wit_count.reset_index().rename({'index':'id'}, axis = 'columns')

wit_count = wit_count[wit_count['Witnesses'].apply(lambda x: x[0:2] not in ['of', 'Of'])]

wit_count = wit_count.query('`Witnesses` != ""') 
wit_count = wit_count.query('`Witnesses` != "Jr."') 
wit_count = wit_count.query('`Witnesses` != "Ph.d"') 
wit_count = wit_count.query('`Witnesses` != "Ph.D"') 
wit_count = wit_count.query('`Witnesses` != "Ph. D."') 
wit_count = wit_count.query('`Witnesses` != "Ii"') 
wit_count = wit_count.query('`Witnesses` != "Iii"') 
wit_count = wit_count.query('`Witnesses` != "Iv"') 
wit_count = wit_count.query('`Witnesses` != "M.D."') 
wit_count = wit_count.query('`Witnesses` != "Ed.D."') 
wit_count = wit_count.query('`Witnesses` != "Md"') 
wit_count = wit_count.query('`Witnesses` != "M.Ed"') 
wit_count = wit_count.query('`Witnesses` != "Esq."') 
wit_count = wit_count.query('`Witnesses` != "J.D."') 
wit_count = wit_count.query('`Witnesses` != "M.P.H."') 
wit_count = wit_count.query('`Witnesses` != "M.P.H"') 
wit_count = wit_count.query('`Witnesses` != "MPH"') 
wit_count = wit_count.query('`Witnesses` != "Mph"') 
wit_count = wit_count.query('`Witnesses` != "P.E."') 
wit_count = wit_count.query('`Witnesses` != "R.N."') 
wit_count = wit_count.query('`Witnesses` != "M.A."') 
wit_count = wit_count.query('`Witnesses` != "Sr."') 
wit_count = wit_count.query('`Witnesses` != "M.B.A."') 
wit_count = wit_count.query('`Witnesses` != "Mba"') 
wit_count = wit_count.query('`Witnesses` != "JR."') 
wit_count = wit_count.query('`Witnesses` != "Jr."') 
wit_count = wit_count.query('`Witnesses` != "Facep"') 
wit_count = wit_count.query('`Witnesses` != "Facp"') 
wit_count = wit_count.query('`Witnesses` != "Faap"') 
wit_count = wit_count.query('`Witnesses` != "F.A.A.P."') 
wit_count = wit_count.query('`Witnesses` != "Fache"') 
wit_count = wit_count.query('`Witnesses` != "Fsa"') 
wit_count = wit_count.query('`Witnesses` != "Rn"') 
wit_count = wit_count.query('`Witnesses` != "Usn"') 
wit_count = wit_count.query('`Witnesses` != "Usa"') 
wit_count = wit_count.query('`Witnesses` != "Drph"') 
wit_count = wit_count.query('`Witnesses` != "Msc"') 
wit_count = wit_count.query('`Witnesses` != "Msw"') 
wit_count = wit_count.query('`Witnesses` != "Dvm"') 
wit_count = wit_count.query('`Witnesses` != "Cpa"') 
wit_count = wit_count.query('`Witnesses` != "Ret.)"') 
wit_count = wit_count.query('`Witnesses` != "Ret"') 
wit_count = wit_count.query('`Witnesses` != "Pe"') 
wit_count = wit_count.query('`Witnesses` != "Pharmd"') 
wit_count = wit_count.query('`Witnesses` != "Pharm.D."') 
wit_count = wit_count.query('`Witnesses` != "A.T.S."') 
wit_count = wit_count.query('`Witnesses` != "D.A.B.T."') 
wit_count = wit_count.query('`Witnesses` != "D.V.M."') 



print(wit_count)
# ^ I would prefer to do a hash of the name but the names are too dirty for now so this works...
wit_count.to_csv("wit_count.csv")
