import io
import os

import boto3
from flask import request, redirect, render_template, jsonify, send_file, make_response, session, send_from_directory
from werkzeug.utils import secure_filename

from app import app

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
    # files = app.s3.list_objects(Bucket=BUCKET)["Contents"]
    files = app.s3.list_objects(Bucket=BUCKET).get("Contents", [])
    return render_template("index.html", files=files)


@app.route('/add')
def upload_file():
    return render_template('upload_file.html')

#
# @app.route('/upd')
# def update_file():
#     return render_template('update_file.html')


# @app.route("/upload", methods=["POST"])
# def upload():
#     file = request.files["file"]
#     app.s3.upload_fileobj(file, BUCKET, file.filename, ExtraArgs=EXTRA_ARGS)
#     # return jsonify({"message": f"File {file.filename} uploaded successfully"})
#     # session['message'] = f"{file.filename} has been uploaded successfully"
#     return redirect("/")

@app.route("/upload", methods=["POST", "PUT"])
def upload():
    file = request.files["file"]
    response = app.s3.list_objects_v2(Bucket=BUCKET, Prefix=file.filename)
    if 'Contents' in response:
        for obj in response['Contents']:
            if obj['Key'] == file.filename:
                # File exists, make PUT request
                app.s3.put_object(Bucket=BUCKET, Key=file.filename, Body=file)
                print(f'{file.filename} has been updated')
                return jsonify({"message": f"File {file.filename} updated successfully"})
    else:
        app.s3.upload_fileobj(file, BUCKET, file.filename, ExtraArgs=EXTRA_ARGS)
        print(f'{file.filename} has been created')
        return jsonify({"message": f"File {file.filename} uploaded successfully"})


@app.route("/download", methods=["GET"])
def download():
    file_name = request.args.get("file_name")
    local_path = f"downloads/{file_name}"
    if os.path.exists(local_path):
        return jsonify({"message": f"File {file_name} already exists locally"})
    else:
        transfer = boto3.s3.transfer.S3Transfer(app.s3)
        transfer.download_file(BUCKET, file_name, local_path)
        if check_file_size(file_name, local_path):
            return jsonify({"message": f"File {file_name} downloaded successfully"})
        else:
            return jsonify({"error": f"File {file_name} downloaded not completely"})
    # return redirect("/")

# @app.route("/update", methods=["PUT"])
# def update():
#     file_name = request.args.get("file_name")
#     try:
#         with open(file_name, "rb") as data:
#             app.s3.put_object(Bucket=BUCKET, Key=file_name, Body=data)
#             return jsonify({"message": f"File {file_name} updated successfully"})
#     except Exception as e:
#         return jsonify({"message": str(e)})


@app.route("/delete", methods=["GET", "DELETE"])
def delete():
    file_name = request.args.get("file_name")
    app.s3.delete_object(Bucket=BUCKET, Key=file_name)
    return jsonify({"message": f"File {file_name} deleted successfully"})
    # return redirect("/")

# def upload_file(file_name, bucket):
#     object_name = file_name
#     response = app.s3.upload_file(file_name, bucket, object_name, ExtraArgs=EXTRA_ARGS)
#     # flash(
#     #     f"File {file_name} has been uploaded successfully to {bucket} as {object_name}"
#     # )
#     return response
#
#
# @app.route("/")
# def list_files():
#     # Get the list of files in the S3 bucket
#     files = app.s3.list_objects(Bucket=BUCKET)["Contents"]
#     return render_template("index.html", files=files)
#
#
# @app.route('/add')
# def add_file():
#     return render_template('upload_file.html')
#
#
# @app.route("/upload", methods=["POST"])
# def upload():
#     f = request.files["file"]
#     f.save(os.path.join(UPLOAD_FOLDER, secure_filename(f.filename)))
#     upload_file(f"{UPLOAD_FOLDER}/{secure_filename(f.filename)}", BUCKET)
#     return redirect("/")
#
#
# @app.route("/update/<file_name>", methods=["PUT"])
# def update_file(file_name):
#     # Get the file from the PUT request
#     # file = request.data
#     # Get the bucket name
#     # bucket_name = BUCKET
#     try:
#         # Update the file in S3
#         app.s3.put_object(
#             Bucket=BUCKET,
#             Key=file_name,
#             Body=request.data
#         )
#         return redirect("/")
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
