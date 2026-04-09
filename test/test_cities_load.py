import requests
import os

from dotenv import load_dotenv

load_dotenv()


def test_currency_load():
    url = "http://api.travelpayouts.com/data/ru/cities.json"
    
    headers = {'X-Access-Token': os.getenv("TOKEN")}
    response = requests.request("GET", url, headers=headers)
    assert response.status_code == 200
    