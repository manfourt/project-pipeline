import boto3
s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="admin",
    aws_secret_access_key="password"
)
s3.upload_file(
    "../data/data_air_cities_100_v20260617.csv",
    "eco-data",
    "raw/data_air_cities.csv"
)
s3.upload_file(
    "../data/data_air_cities.parquet",
    "eco-data",
    "processed/data_air_cities.parquet"
)