import os

from flask import Flask
# from flask_restful import Api
import boto3
from dotenv import load_dotenv

load_dotenv()

access_key = os.getenv('AWS_ACCESS_KEY')
secret_key = os.getenv('AWS_SECRET_KEY')

app = Flask(__name__)


@app.route('/')
def list_bucket():
    s3 = boto3.resource(
        service_name='s3',
        region_name='eu-central-1',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    lst = [bucket.name for bucket in s3.buckets.all()]

    return lst


if __name__ == '__main__':
    app.run()
