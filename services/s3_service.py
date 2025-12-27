import boto3
from uuid import uuid4
from core.configs import settings

s3_client = boto3.client(
    "s3",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

def upload_avatar_to_s3(file, user_id: int) -> str:
    extension = file.filename.split('.')[-1]
    key = f"avatars/{user_id}-{uuid4()}.{extension}"

    s3_client.upload_fileobj(
        file.file,
        settings.AWS_S3_BUCKET,
        key,
        ExtraArgs={"ContentType": file.content_type}
    )

    return key


def generate_presigned_url(key: str, expires_in: int = 3600) -> str:
    return s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": settings.AWS_S3_BUCKET,
            "Key": key
        },
        ExpiresIn=expires_in
    )
