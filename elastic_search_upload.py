import pandas as pd
from elasticsearch import Elasticsearch, helpers
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

es = Elasticsearch(
    cloud_id=config['ELASTIC']['cloud_id'],
    http_auth=(config['ELASTIC']['user'], config['ELASTIC']['password'])
)

current_transcripts = pd.read_csv("New_T_File.csv")
current_transcripts = current_transcripts.iloc[0:] 

search_length = len(current_transcripts)

for i, row in enumerate(current_transcripts.itertuples(index=False)):

    print(f"{i} / {search_length} => {i / search_length} | {row[2]}")
    result = es.search(
    index='first-view',
    body = {
        'query': {
            "term": {
            "url": row[2]
            }
        }
    }
    )

    data = result['hits']['hits']

    if data == []:
        print(f"Need to upload {row[2]}")
        doc = {
            'name': row[1],
            'url': row[2],
            'text': row[3]
        }
        resp = es.index(index="first-view",  document=doc)
        print(resp['result'])
    else:
        print(f"{row[2]} Already In")
