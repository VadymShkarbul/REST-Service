import os

import boto3
from flask import Flask, render_template, request, redirect, send_file
# from s3_functions import upload_file, show_image
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
BUCKET = "my-shiny-new-bucket"

access_key = os.getenv('AWS_ACCESS_KEY')
secret_key = os.getenv('AWS_SECRET_KEY')

extra_args = {'ContentType': 'application/octet-stream'}

app.s3 = boto3.client(
        's3',
        region_name='eu-central-1',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

def upload_file(file_name, bucket):
    object_name = file_name
    # s3_client = boto3.client(
    #     's3',
    #     region_name='eu-central-1',
    #     aws_access_key_id=access_key,
    #     aws_secret_access_key=secret_key
    # )
    response = app.s3.upload_file(
        file_name,
        bucket,
        object_name,
        ExtraArgs=extra_args
    )
    return response


def show_image(bucket):
    # s3_client = boto3.client(
    #     's3',
    #     region_name='eu-central-1',
    #     aws_access_key_id=access_key,
    #     aws_secret_access_key=secret_key
    # )
    public_urls = []
    try:
        for item in app.s3.list_objects(Bucket=bucket)['Contents']:
            presigned_url = app.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': item['Key']},
                ExpiresIn=100
            )
            public_urls.append(presigned_url)
    except Exception as e:
        pass
    # print("[INFO] : The contents inside show_image = ", public_urls)
    return public_urls


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/upload", methods=['POST'])
def upload():
    f = request.files['file']
    print(f.filename)
    f.save(os.path.join(UPLOAD_FOLDER, secure_filename(f.filename)))
    upload_file(f"{UPLOAD_FOLDER}/{secure_filename(f.filename)}", BUCKET)
    return redirect("/")


@app.route("/pics")
def list():
    contents = show_image(BUCKET)
    return render_template('collection.html', contents=contents)


if __name__ == '__main__':
    app.run(debug=True)
