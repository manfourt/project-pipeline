import s3fs
import pandas as pd
storage_options = {
    "key": "admin",
    "secret": "password",
    "client_kwargs": {
        "endpoint_url": "http://localhost:9000"
    }
}
df_from_minio = pd.read_parquet(
    "s3://eco-data/processed/data_air_cities.parquet",
    storage_options=storage_options
)

result1 = df_from_minio.groupby(
    "region"
)["air_solid_emissions"].mean().dropna().sort_values(ascending=False).reset_index()
print(result1)

result2 = (
    df_from_minio[df_from_minio["air_general_level"] >= 0]
    .groupby("region")
    .agg(
        avg_level=("air_general_level", "mean"),
        cities_count=("city", "nunique")
    )
    .reset_index()
    .sort_values("avg_level", ascending=False)
)
print(result2)

result3 = (
    df_from_minio
    .groupby("city")
    ["air_co_emissions"].mean().dropna().sort_values(ascending=False).head(50).reset_index()
)
print(result3)

result4 = (
    df_from_minio
    .groupby("year")
    .agg(
        avg_level=("air_so_emissions", "mean"),
        max_level=("air_so_emissions", "max"),
        min_level=("air_so_emissions", "min")
    )
    .dropna()
    .reset_index()
    .sort_values("year", ascending=True)
)
print(result4)

result5 = (
    df_from_minio[df_from_minio["air_no_emissions"] >= 0]
    .groupby("region")["air_no_emissions"]
    .sum()
    .dropna()
    .sort_values(ascending=False)
    .head(50)
    .reset_index()
)
print(result5)

result1.to_parquet(
    "s3://eco-data/analytics/avg_solid_by_region.parquet",
    storage_options=storage_options,
    index=False
)

result2.to_parquet(
    "s3://eco-data/analytics/region_statistics.parquet",
    storage_options=storage_options,
    index=False
)

result3.to_parquet(
    "s3://eco-data/analytics/top_cities_by_co.parquet",
    storage_options=storage_options,
    index=False
)

result4.to_parquet(
    "s3://eco-data/analytics/air_so_emissions_level_by_year.parquet",
    storage_options=storage_options,
    index=False
)

result5.to_parquet(
    "s3://eco-data/analytics/top_regions_by_no.parquet",
    storage_options=storage_options,
    index=False
)