import pandas as pd
import numpy as np


df_market = pd.read_csv("SMADIMO-GP-2/data/market.xlsx - Sheet1.csv")
df_market.drop(
    ["Домен", "Другие поддерживаемые языки", "Язык по умолчанию (Список поддерживаемых языков)", "Другие поддерживаемые валюты"], axis=1, inplace=True
)
df_market.drop([22, 23, 24], axis=0, inplace=True)
df_market.reset_index(drop=True, inplace=True)
df_market.to_csv("SMADIMO-GP-2/data/market_prepared.csv", index=False)
