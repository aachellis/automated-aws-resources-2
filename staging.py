import boto3
import json
import botocore

with open("configuarions.json") as f:
    conf = json.load(f)

s3 = boto3.client("s3", region_name=conf["region"])

bucket_name = conf["name"].replace(' ', '-')

try:
    bucket = s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
            'LocationConstraint': conf["region"]
        },
    )
except botocore.exceptions.ClientError as error:
    if error.response['Error']['Code'] == 'BucketAlreadyExists' or error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
        pass 
    else:
        raise error