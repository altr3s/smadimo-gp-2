import requests
import pandas as pd
import os
import json
from dotenv import load_dotenv

load_dotenv()

url = "http://api.travelpayouts.com/v1/airline-directions"
query = {
    "airline_code": "R3"
}

headers = {'X-Access-Token': os.getenv("TOKEN")}
response = requests.request("GET", url, headers=headers, params=query)

with open("SMADIMO-GP-2/data/airline_directions.json", "w") as f:
    json.dump(response.json(), f, ensure_ascii=False, indent=4)
    
url1 = 'https://api.travelpayouts.com/data/en/airlines.json'

headers = {'X-Access-Token': os.getenv("TOKEN")}
response = requests.request("GET", url1, headers=headers)

with open("SMADIMO-GP-2/data/airline_info.json", "w") as f:
    json.dump(response.json(), f, ensure_ascii=False, indent=4)