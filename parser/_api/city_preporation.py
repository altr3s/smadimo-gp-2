import pandas as pd

df_wiki = pd.read_csv("SMADIMO-GP-2/data/wiki-ru-cities.csv")
df_cities_aviasales = pd.read_csv("SMADIMO-GP-2/data/cities-aviasales.csv")

df_cities_aviasales = df_cities_aviasales[df_cities_aviasales["has_flightable_airport"] == True]
merged_city = pd.merge(df_cities_aviasales, df_wiki, how='inner', left_on="name", right_on="city")

merged_city.rename(columns={"Unnamed: 0": "population_rating", "code": "IATA_code"}, inplace=True)
merged_city.drop(["city"], axis=1, inplace=True)
merged_city.sort_values(by="population_rating", ascending=True, inplace=True)
merged_city.reset_index(drop=True, inplace=True)
merged_city.drop(0, axis=0, inplace=True)

merged_city.to_csv("SMADIMO-GP-2/data/_api/cities_prepared.csv", index=False)