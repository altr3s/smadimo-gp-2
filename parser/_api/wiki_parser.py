import requests
import pandas as pd
from bs4 import BeautifulSoup

section_ids = [
    "Города_с_населением_более_1_млн_человек_(крупнейшие_города)",
    "Города_с_населением_250_тысяч_—_1_млн_человек_(крупные_города)",
    "Города_с_населением_500_тысяч_—_1_млн_человек",
    "Города_с_населением_250—500_тысяч_человек",
    "Города_с_населением_100—250_тысяч_человек_(большие_города)",
    "Города_с_населением_50_—_100_тысяч_человек_(средние_города)",
    "Города_с_населением_менее_50_тыс._человек_(малые_города)"
]

url = "https://ru.wikipedia.org/wiki/Города_России"

headers = {
    "User-Agent": "Mozilla/5.0",
}

response = requests.get(url, headers=headers, timeout=10)

soup = BeautifulSoup(response.text, "html.parser")

rows = []

for section_id in section_ids:
    header = soup.find(["h2", "h3"], id=section_id)

    if not header: continue

    table = None
    for next_headers in header.find_all_next():
        if next_headers.name in ["h2", "h3"]: break

        if next_headers.name == "table" and "sortable" in next_headers.get("class"):
            table = next_headers
            break

    if not table: continue

    for tr in table.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 2: continue
        city = tds[1].get_text().strip()
        rows.append(city)

df = pd.DataFrame({"city": rows}).drop_duplicates().reset_index(drop=True)
df.to_csv("SMADIMO-GP-2/data/_api/wiki-ru-cities.csv")