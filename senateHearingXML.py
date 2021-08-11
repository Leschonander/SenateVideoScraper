import requests
import pandas as pd
from datetime import datetime

def get_todays_senate_hearings():

    current_date = datetime.today().strftime("%Y-%m-%d")

    url = "https://api.propublica.org/congress/v1/117/committees/hearings.json"
    # https://projects.propublica.org/api-docs/congress-api/committees/ (Get Recent Committee Hearings)

    API_KEY = "sw8CjOT4YeI690S9byQ2Qa3XAuF1vbUClFcA8dOK"
    headers = {
        "X-API-Key": API_KEY
    }

    response = requests.get(url, headers = headers)

    data = response.json()
    hearings = data["results"][0]["hearings"]

    senate_hearings = []
    for h in hearings:
        if h["chamber"] == "Senate":
            senate_hearings.append(h)

    senate_hearings_data = pd.DataFrame(senate_hearings)
    today_senate_hearings_data = senate_hearings_data.query(f'`date` != "{current_date}"')

    return today_senate_hearings_data

print(get_todays_senate_hearings())