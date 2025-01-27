import boto3
from storages.backends.s3boto3 import S3Boto3Storage

from backend.settings.base import (
    AWS_ACCESS_KEY_ID,
    AWS_S3_REGION_NAME,
    AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME_PRIVATE,
    ENV,
)

if not ENV.application.use_local_s3:
    bucket = ''
    access_key = ''
    secret_key =''
    region = ''
else:
    bucket = AWS_STORAGE_BUCKET_NAME_PRIVATE
    access_key = AWS_ACCESS_KEY_ID
    secret_key = AWS_SECRET_ACCESS_KEY
    region = AWS_S3_REGION_NAME
    

class PrivateS3Boto3Storage(S3Boto3Storage):
    """
        Custom storage backend used for private files
    """
    def __init__(self, *args, **kwargs):
        kwargs['bucket_name'] = bucket
        super().__init__(*args, **kwargs)

    def url(self, name):
        s3_client = boto3.client(
            's3',
            aws_access_key_id = access_key,
            aws_secret_access_key = secret_key,
            region_name = region
        )

        return s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': f'media/{name}'},
            ExpiresIn=60  # url expiration time in seconds
        )
    

def get_private_storage():
    if not ENV.application.use_local_s3:
        # use django's default file system storage
        return None
    return PrivateS3Boto3Storage()
    
