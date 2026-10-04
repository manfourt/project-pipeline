import pandas as pd
df = pd.read_csv('../data/data_air_cities_100_v20260617.csv')
df.to_parquet(
    "../data/data_air_cities.parquet",
    index=False
)