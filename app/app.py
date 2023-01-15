import hashlib
import os

import boto3
from botocore import exceptions
from flask import request, render_template, jsonify, Response
from werkzeug.utils import secure_filename

from app import app

UPLOAD_DIR = "uploads"
DOWNLOAD_DIR = "downloads"
BUCKET = app.config["S3_BUCKET_NAME"]
EXTRA_ARGS = {"ContentType": "application/octet-stream"}


def check_file(key: str, local_path: str) -> bool:
    """
    The function checks the size and content of the local file and
    the file in the cloud and returns a boolean value
    """
    s3_file_size = app.s3.head_object(Bucket=BUCKET, Key=key)["ContentLength"]
    local_file_size = os.path.getsize(local_path)

    local_hash = hashlib.sha256()
    with open(local_path, "rb") as f:
        local_hash.update(f.read())
    local_file_hash = local_hash.hexdigest()
    s3_hash = hashlib.sha256()
    s3_object = app.s3.get_object(Bucket=BUCKET, Key=key)
    s3_hash.update(s3_object["Body"].read())
    s3_object_hash = s3_hash.hexdigest()

    if local_file_hash == s3_object_hash and s3_file_size == local_file_size:
        return True
    return False


@app.route("/")
def list_files() -> str:
    files = app.s3.list_objects(Bucket=BUCKET).get("Contents", [])
    return render_template("index.html", files=files)


@app.route("/add")
def upload_file() -> str:
    return render_template("upload_file.html")


@app.route("/upload", methods=["POST", "PUT"])
def upload() -> Response:
    """
    If I understand the boto3 documentation correctly, under the hood
    upload_file() and upload_fileobj() methods work in such a way
    that if the file exists - it is updated (PUT), if not - it is uploaded(POST).
    In my opinion, using S3Transfer is safer from the point of view of data
    integrity, will better work with larger files(IMHO) and the condition is met:
    the data is available via GET immediately after the PUT is completed
    """
    file = request.files["file"]
    if request.files["file"].filename == "":
        return jsonify({"error": "No file selected"})
    else:
        file_name = secure_filename(file.filename)
        local_path = f"{UPLOAD_DIR}/{file_name}"
        file.save(local_path)
        transfer = boto3.s3.transfer.S3Transfer(app.s3)

        try:
            app.s3.head_object(Bucket=BUCKET, Key=file_name)
        except exceptions.ClientError:
            transfer.upload_file(local_path, BUCKET, file_name, extra_args=EXTRA_ARGS)
            response = jsonify({"message": f"File {file_name} uploaded successfully"})
        else:
            transfer.upload_file(local_path, BUCKET, file_name, extra_args=EXTRA_ARGS)
            response = jsonify({"message": f"File {file_name} updated successfully"})
        finally:
            os.remove(local_path)

        return response


@app.route("/download", methods=["GET"])
def download() -> Response:
    file_name = request.args.get("file_name")
    local_path = f"{DOWNLOAD_DIR}/{file_name}"
    if os.path.exists(local_path) and check_file(file_name, local_path):
        return jsonify({"message": f"File {file_name} already exists locally"})
    else:
        transfer = boto3.s3.transfer.S3Transfer(app.s3)
        transfer.download_file(BUCKET, file_name, local_path)
        return jsonify({"message": f"File {file_name} downloaded successfully"})


@app.route("/delete", methods=["GET", "DELETE"])
def delete() -> Response:
    file_name = request.args.get("file_name")
    app.s3.delete_object(Bucket=BUCKET, Key=file_name)
    return jsonify({"message": f"File {file_name} deleted successfully"})


if __name__ == "__main__":
    app.run()
