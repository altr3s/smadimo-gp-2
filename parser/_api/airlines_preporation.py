import pandas as pd
import json
import os
import dotenv
import requests
import time
import tqdm

url = "http://api.travelpayouts.com/v1/airline-directions"

dotenv.load_dotenv()

def preporation_wiki(df):
    df = df[~df['ИАТА'].isna()]
    df.drop('ИНН', axis=1, inplace=True)
    df.rename(columns={'ИАТА': 'iata_code'}, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def preporation_airlines():
    airlanes_info = json.load(open("SMADIMO-GP-2/data/airline_info.json", "r"))
    airlanes_info_df = pd.DataFrame(airlanes_info)
    airlanes_info_df.drop('name_translations', axis=1, inplace=True)
    return airlanes_info_df

def add_top_destanations(iata_code, df):
    query = {
        "airline_code": iata_code
    }

    headers = {'X-Access-Token': os.getenv("TOKEN")}
    response = requests.request("GET", url, headers=headers, params=query)

    answer = []
    with open("SMADIMO-GP-2/data/airline_directions.json", "w") as f:
        for k, v in response.json()['data'].items():
            answer.append(
                (k, v)
            )
    answer.sort(key= lambda x: x[1], reverse=True)
    
    df.loc[df["iata_code"] == iata_code, "top_destinations"] = str(answer)
    time.sleep(1)
    
    

airlanes_info_df = preporation_airlines()
ru_airlines = preporation_wiki(
    pd.read_csv("SMADIMO-GP-2/data/_api/Список_действующих_авиакомпаний_России_—_Википедия.csv")
)
airlines = pd.merge(ru_airlines, airlanes_info_df, left_on='iata_code', right_on='code', how='inner')
airlines.drop(['code', 'Код в России'], axis=1, inplace=True)
airlines.rename(columns={'name': 'name_en', 'Бренд': 'name_ru'}, inplace=True)
airlines.drop([14, 16, 31], inplace=True)
airlines.reset_index(drop=True, inplace=True)

for iata_code in tqdm.tqdm(airlines["iata_code"], total=len(airlines['iata_code'])):
    add_top_destanations(iata_code, airlines)
    
airlines.to_csv("SMADIMO-GP-2/data/_api/airlines_russia.csv", index=False)