import requests
import os

from dotenv import load_dotenv

load_dotenv()


def test_currency_load():
    url = 'https://api.travelpayouts.com/data/en/airlines.json'
    
    headers = {'X-Access-Token': os.getenv("TOKEN")}
    response = requests.request("GET", url, headers=headers)
    assert response.status_code == 200
    