import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = True
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


def create_dir(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
