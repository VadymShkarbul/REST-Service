import os

import boto3
from flask import request, render_template, jsonify
from werkzeug.utils import secure_filename

from app import app

UPLOAD_DIR = "uploads"
DOWNLOAD_DIR = "downloads"
BUCKET = app.config["S3_BUCKET_NAME"]
EXTRA_ARGS = {"ContentType": "application/octet-stream"}


# def check_file_exists(file_name):
#     try:
#         response = app.s3.list_objects_v2(Bucket=BUCKET, Prefix=file_name)
#         return response['KeyCount'] > 0
#     except:
#         return False

def check_file_size(key, local_path):
    s3_file_size = app.s3.head_object(Bucket=BUCKET, Key=key)["ContentLength"]
    local_file_size = os.path.getsize(local_path)
    if s3_file_size != local_file_size:
        return False
    else:
        return True


@app.route("/")
def list_files():
    files = app.s3.list_objects(Bucket=BUCKET).get("Contents", [])
    return render_template("index.html", files=files)


@app.route('/add')
def upload_file():
    return render_template('upload_file.html')


@app.route("/upload", methods=["POST", "PUT"])
def upload():
    if request.files["file"].filename == "":
        return jsonify({"error": "No file selected"})
    else:
        file = request.files["file"]
        print(file.filename)
        file_name = secure_filename(file.filename)
        response = app.s3.list_objects_v2(Bucket=BUCKET, Prefix=file_name)
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'] == file_name:
                    # File exists, make PUT request
                    app.s3.put_object(Bucket=BUCKET, Key=file_name, Body=file.stream)
                    return jsonify({"message": f"File {file_name} updated successfully"})
                    """
                    If I understand the boto3 documentation correctly, under the hood 
                    the upload_file() and upload_fileobj() methods work in such a way
                    that if the file exists - it is updated, if not - it is uploaded. 
                    I left this code because in the condition of the test task 
                    I had to implement the put operation and it was interesting 
                    to work with this method as well ;)
                    """
        else:
            # File does not exist, make POST request
            local_path = f"{UPLOAD_DIR}/{file_name}"
            file.save(local_path)
            transfer = boto3.s3.transfer.S3Transfer(app.s3)
            transfer.upload_file(local_path, BUCKET, file_name)
            if check_file_size(file_name, local_path):
                os.remove(local_path)
                return jsonify({"message": f"File {file_name} uploaded successfully"})
            os.remove(local_path)
            return jsonify({"error": f"File {file_name} uploaded not completely"})
            """
            # I chose this method because, in my opinion, using S3Transfer is safer
            # from the point of view of data integrity and will allow working with larger files
            # I haven't found a more elegant way to do this...
            Flask-Uploads + boto3?
            """
            # app.s3.upload_fileobj(file.stream, BUCKET, file_name)


@app.route("/download", methods=["GET"])
def download():
    file_name = request.args.get("file_name")
    local_path = f"{DOWNLOAD_DIR}/{file_name}"
    if os.path.exists(local_path):
        return jsonify({"message": f"File {file_name} already exists locally"})
    else:
        transfer = boto3.s3.transfer.S3Transfer(app.s3)
        transfer.download_file(BUCKET, file_name, local_path)
        if check_file_size(file_name, local_path):
            return jsonify({"message": f"File {file_name} downloaded successfully"})
        else:
            return jsonify({"error": f"File {file_name} downloaded not completely"})


@app.route("/delete", methods=["GET", "DELETE"])
def delete():
    file_name = request.args.get("file_name")
    app.s3.delete_object(Bucket=BUCKET, Key=file_name)
    return jsonify({"message": f"File {file_name} deleted successfully"})


if __name__ == '__main__':
    app.run()
