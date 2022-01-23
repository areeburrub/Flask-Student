import boto3
from flask import session
import os

AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_DEFAULT_REGION = os.environ['AWS_DEFAULT_REGION']
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']


def _get_s3_resource():
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        return boto3.resource(
            's3',
            aws_access_key_id= AWS_ACCESS_KEY_ID,
            aws_secret_access_key= AWS_SECRET_ACCESS_KEY,
            region_name= AWS_DEFAULT_REGION
        )
    else:
        return boto3.resource('s3')


def get_bucket():
    s3_resource = _get_s3_resource()
    bucket = S3_BUCKET_NAME

    return s3_resource.Bucket(bucket)


def get_buckets_list():
    client = boto3.client('s3')
    return client.list_buckets().get('Buckets')
