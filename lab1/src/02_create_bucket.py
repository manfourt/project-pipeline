import boto3
s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="admin",
    aws_secret_access_key="password"
)

bucket_name = "eco-data"
s3.create_bucket(
    Bucket=bucket_name)
response = s3.list_buckets()

for bucket in response["Buckets"]:
    print(bucket["Name"])
