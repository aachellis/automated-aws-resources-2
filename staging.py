import boto3
import json
import uuid
import botocore

with open("configuarions.json") as f:
    conf = json.load(f)

ssm = boto3.client('ssm', region_name=conf["region"])
s3 = boto3.client("s3", region_name=conf["region"])

try:
    bucket_name = ssm.get_parameter(Name=f"/{conf['name'].replace(' ', '-')}/bucket_name")['Parameter']['Value']
except botocore.exceptions.ClientError as error:
    if error.response["Error"]["Code"] == "ParameterNotFound":
        bucket_name = conf["name"].replace(' ', '-') + "-" + str(uuid.uuid4()) + "-" + conf["region"]
        ssm.put_parameter(Name=f"/{conf['name'].replace(' ', '-')}/bucket_name", Value=bucket_name, Type='String')
    else:
        raise error

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