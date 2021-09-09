import pandas as pd
import numpy as np
import re
import os

master_file_data_frame = pd.read_csv("./SenateVideoFiles/MasterFile.csv")

gov_info_senate_hearing_files = os.listdir("./GovInfoHearings")
total_gov_info_senate_hearing = []
for f in gov_info_senate_hearing_files:
    file_path = "./GovInfoHearings/" + f
    data_frame = pd.read_csv(file_path, skiprows=2)
    total_gov_info_senate_hearing.append(data_frame)

total_gov_info_senate_hearing = pd.concat(total_gov_info_senate_hearing)
total_gov_info_senate_hearing = total_gov_info_senate_hearing.rename(columns={"title": "Title"})

master_file_data_frame['Title'] = master_file_data_frame['Title'].str.replace('"', '')

title_queries = [
    (master_file_data_frame['Title'].str.contains('Full Committee hearing entitled', case=False, regex=False, na=False), master_file_data_frame['Title'].str.replace('Full Committee hearing entitled', '').str.replace('“', '').str.replace('.”', '')),
    (master_file_data_frame['Title'].str.contains('Full Committee Hearing entitled,', case=False, regex=False, na=False), master_file_data_frame['Title'].str.replace('Full Committee Hearing entitled', '').str.replace('“', '').str.replace('.”', '')),
    (master_file_data_frame['Title'].str.contains('Full Committee Hearing : ', case=False, regex=False, na=False), master_file_data_frame['Title'].str.replace('Full Committee Hearing : ', '').str.strip()),
    (master_file_data_frame['Title'].str.contains('Subcommittee Hearing:', case=False, regex=False, na=False), master_file_data_frame['Title'].str.replace('Subcommittee Hearing:', '').str.strip()),
    (master_file_data_frame['Title'].str.contains('Subcommittee Hearing : ', case=False, regex=False, na=False), master_file_data_frame['Title'].str.replace('Subcommittee Hearing : ', '').str.strip()),
    (master_file_data_frame['Title'].str.contains('Business Meeting:', case=False, regex=False, na=False), master_file_data_frame['Title'].str.replace('Business Meeting:', '').str.replace('"', '')),
    (master_file_data_frame['Title'].str.contains('POSTPONED', case=False, regex=False, na=False), master_file_data_frame['Title'].str.replace('POSTPONED', '' ).replace(':', '')),
    (master_file_data_frame['Title'].str.contains('TIME CHANGE', case=False, regex=False, na=False), master_file_data_frame['Title'].str.replace('TIME CHANGE', '').replace(':', '')),
    (master_file_data_frame['Title'].str.contains('CANCELLED', case=False, regex=False, na=False), master_file_data_frame['Title'].str.replace('CANCELLED', '').replace(':', '')),
    (master_file_data_frame['Title'].str.contains('Full Committee Hearing:', case=False, regex=False, na=False), master_file_data_frame['Title'].str.replace('Full Committee Hearing:', '').replace(':', '')),
    (master_file_data_frame['Title'].str.contains('Field Hearing:', case=False, regex=False, na=False), master_file_data_frame['Title'].str.replace('Field Hearing:', '').replace(':', '')),
]
title_requirment, title_result = zip(*title_queries)

master_file_data_frame["Title"] = np.select(title_requirment, title_result, master_file_data_frame["Title"])

master_file_data_frame['Title'] = master_file_data_frame['Title'].str.replace('---', '').str.strip()


master_file_data_frame[["Date","Title"]].to_csv("Test.csv")
joined_df = master_file_data_frame.merge(total_gov_info_senate_hearing, on='Title', how='left')
joined_df = joined_df.dropna(subset=['publishdate'])
joined_df = joined_df.drop_duplicates(subset=['URL'])
print(joined_df)
# joined_df.to_csv("JoinedFileTest.csv")