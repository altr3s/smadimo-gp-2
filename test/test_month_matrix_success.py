import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_month_matrix_success():
    url = "http://api.travelpayouts.com/v2/prices/month-matrix"
    headers = {"X-Access-Token": os.getenv("TOKEN")}
    query = {
        "origin": "MOW",
        "month": "2026-06-01",
        "destination": "LED",
        "show_to_affiliates": "false",
        "one_way": "true",
        "direct": "true",
        "market": "ru",
        "currency": "rub",
    }

    response = requests.get(url, headers=headers, params=query, timeout=30)
    
    data = response.json()
    assert response.status_code == 200
    
    assert 'success' in data
    assert 'data' in data
    assert isinstance(data['data'], list)
    assert data['success'] is True
