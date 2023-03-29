import boto3
import json
import uuid

with open("configuarions.json") as f:
    conf = json.load(f)

s3 = boto3.client("s3", region_name=conf["region"])

bucket_name = conf["name"].replace(' ', '-') + "-" + str(uuid.uuid4())

bucket = s3.create_bucket(
    Bucket=bucket_name,
    CreateBucketConfiguration={
        'LocationConstraint': conf["region"]
    },
)