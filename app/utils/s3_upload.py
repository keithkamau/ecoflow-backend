"""S3 upload helper — stub. Member 4 uses this for proof-of-pickup photos."""
from typing import Optional
import boto3
from app.config import settings


def upload_file(file_bytes: bytes, filename: str, content_type: str = "image/jpeg") -> Optional[str]:
    """Upload bytes to S3 and return the public URL, or None on failure."""
    try:
        client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        client.put_object(
            Bucket=settings.AWS_BUCKET_NAME,
            Key=filename,
            Body=file_bytes,
            ContentType=content_type,
        )
        return f"https://{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{filename}"
    except Exception:
        return None
