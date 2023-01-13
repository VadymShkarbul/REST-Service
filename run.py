# import os
# import secrets
#
# import boto3
# from boto3 import Session
# from flask import Flask, render_template, request, redirect, send_file, flash, jsonify
#
# # from s3_functions import upload_file, show_image
# from werkzeug.utils import secure_filename
# from dotenv import load_dotenv
#
# load_dotenv()
# FLASK_SECRET_KEY = secrets.token_hex(16)
#
# app = Flask(__name__)
# # app.config['SESSION_TYPE'] = 'memcached'
# app.config["SECRET_KEY"] = FLASK_SECRET_KEY
# sess = Session()
#
# UPLOAD_FOLDER = "uploads"
# BUCKET = "my-shiny-new-bucket"
#
# access_key = os.getenv("AWS_ACCESS_KEY")
# secret_key = os.getenv("AWS_SECRET_KEY")
#
# extra_args = {"ContentType": "application/octet-stream"}
#
# app.s3 = boto3.client(
#     "s3",
#     region_name="eu-central-1",
#     aws_access_key_id=access_key,
#     aws_secret_access_key=secret_key,
# )
#
#
# def upload_file(file_name, bucket):
#     object_name = file_name
#     # s3_client = boto3.client(
#     #     's3',
#     #     region_name='eu-central-1',
#     #     aws_access_key_id=access_key,
#     #     aws_secret_access_key=secret_key
#     # )
#     response = app.s3.upload_file(file_name, bucket, object_name, ExtraArgs=extra_args)
#     flash(
#         f"File {file_name} has been uploaded successfully to {bucket} as {object_name}"
#     )
#     return response
#
#
# def show_image(bucket):
#     # s3_client = boto3.client(
#     #     's3',
#     #     region_name='eu-central-1',
#     #     aws_access_key_id=access_key,
#     #     aws_secret_access_key=secret_key
#     # )
#     public_urls = []
#     try:
#         for item in app.s3.list_objects(Bucket=bucket)["Contents"]:
#             presigned_url = app.s3.generate_presigned_url(
#                 "get_object",
#                 Params={"Bucket": bucket, "Key": item["Key"]},
#                 ExpiresIn=100,
#             )
#             public_urls.append(presigned_url)
#     except Exception as e:
#         pass
#     # print("[INFO] : The contents inside show_image = ", public_urls)
#     return public_urls
#
#
# # @app.route("/")
# # def home():
# #     return render_template('index.html')
# @app.route("/")
# def list_files():
#     # Get the list of files in the S3 bucket
#     # bucket_name = '<your-bucket-name>'
#     files = app.s3.list_objects(Bucket=BUCKET)["Contents"]
#     return render_template("index.html", files=files)
#
#
# @app.route("/upload", methods=["POST"])
# def upload():
#     f = request.files["file"]
#     print(f.filename)
#     f.save(os.path.join(UPLOAD_FOLDER, secure_filename(f.filename)))
#     upload_file(f"{UPLOAD_FOLDER}/{secure_filename(f.filename)}", BUCKET)
#     return redirect("/")
#
#
# @app.route("/update/<file_name>", methods=["PUT"])
# def update_file(file_name):
#     # Get the file from the PUT request
#     file = request.data
#     # Get the bucket name
#     bucket_name = BUCKET
#     try:
#         # Update the file in S3
#         app.s3.put_object(Bucket=bucket_name, Key=file_name, Body=file)
#         return redirect("/files")
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
#
# @app.route("/pics")
# def list():
#     contents = show_image(BUCKET)
#     return render_template("collection.html", contents=contents)

from flask import Flask
# from app import app
# @app.route('/')
# @app.route('/index')
# def index():
#     return "Hello, World!"
#

from app.view import *

if __name__ == '__main__':
    app.run()
