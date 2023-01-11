def upload_file(file_name, bucket):
    object_name = file_name
    s3_client = boto3.client(
        's3',
        region_name='eu-central-1',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    response = s3_client.upload_file(file_name, bucket, object_name)
    return response