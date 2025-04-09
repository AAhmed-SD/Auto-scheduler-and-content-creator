import boto3
from botocore.config import Config
from .config import get_settings

settings = get_settings()

s3_config = Config(
    retries=dict(max_attempts=3),
    connect_timeout=5,
    read_timeout=5
)

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
    config=s3_config
)

def get_s3_client():
    return s3_client

def generate_presigned_url(bucket: str, key: str, expires_in: int = 3600) -> str:
    """Generate a presigned URL for S3 object access."""
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=expires_in
        )
        return url
    except Exception as e:
        raise Exception(f"Failed to generate presigned URL: {str(e)}") 