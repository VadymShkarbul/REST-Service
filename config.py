import os
from dotenv import load_dotenv

# TODO: KISS!
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    DEBUG = True
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
