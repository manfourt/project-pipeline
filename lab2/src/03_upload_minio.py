from pathlib import Path

import boto3

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="admin",
    aws_secret_access_key="password"
)

# свой bucket для лабораторной работы 2
bucket_name = "air-quality"
existing = [bucket["Name"] for bucket in s3.list_buckets()["Buckets"]]
if bucket_name not in existing:
    s3.create_bucket(Bucket=bucket_name)

# raw — исходный JSON из API
s3.upload_file(
    str(DATA_DIR / "air_quality_raw.json"),
    bucket_name,
    "raw/air_quality_raw.json"
)

# processed — обработанные Parquet-файлы
s3.upload_file(
    str(DATA_DIR / "cities.parquet"),
    bucket_name,
    "processed/cities.parquet"
)
s3.upload_file(
    str(DATA_DIR / "air_quality.parquet"),
    bucket_name,
    "processed/air_quality.parquet"
)
