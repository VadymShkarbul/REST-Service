import boto3
from flask import Flask
from config import Config


app = Flask(__name__)
app.config.from_object(Config)

app.s3 = boto3.client(
    "s3",
    region_name=app.config["AWS_REGION"],
    aws_access_key_id=app.config["AWS_ACCESS_KEY"],
    aws_secret_access_key=app.config["AWS_SECRET_KEY"],
)
