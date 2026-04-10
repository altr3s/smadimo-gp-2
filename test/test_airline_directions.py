import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_airline_directions():
    url = "http://api.travelpayouts.com/v1/airline-directions"  
    headers = {'X-Access-Token': os.getenv("TOKEN")}
    query = {
        "airline_code": "UT"
    }

    response = requests.get(url, headers=headers, params=query, timeout=30)
    
    data = response.json()
    assert response.status_code == 200
    
    assert 'success' in data
    assert 'data' in data
    
    assert isinstance(data['data'], dict)
    assert data['success'] is True
