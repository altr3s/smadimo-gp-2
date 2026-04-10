import requests
import pandas as pd
import os
import json
from dotenv import load_dotenv

load_dotenv()

url = "http://yasen.aviasales.ru/adaptors/currency.json"

headers = {'X-Access-Token': os.getenv("TOKEN")}
response = requests.request("GET", url, headers=headers)

with open("SMADIMO-GP-2/data/_api/currency.json", "w") as f:
    json.dump(response.json(), f, indent=4)
