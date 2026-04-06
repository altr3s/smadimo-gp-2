import requests
import pandas as pd
import os


url = "http://api.travelpayouts.com/data/ru/cities.json"
headers = {'x-access-token': os.getenv("TOKEN")}
response = requests.request("GET", url, headers=headers)
rows = []

for city in response.json():
    if city.get("country_code") == "RU":
        rows.append({
            "name": city.get("name"),
            "name_en": city.get("name_translations", {}).get("en"),
            "code": city.get("code"),
            "lat": city.get("coordinates", {}).get("lat"),
            "lon": city.get("coordinates", {}).get("lon"),
            "has_flightable_airport": city.get("has_flightable_airport"),
            "time_zone": city.get("time_zone"),
        })

cities = pd.DataFrame(rows)

cities.to_csv("SMADIMO-GP-2/data/cities-aviasales.csv")