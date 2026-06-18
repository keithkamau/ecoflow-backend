import os
import uuid
import asyncio
from fastapi import UploadFile

from app.config import settings


class StorageService:
    def __init__(self):
        self.use_s3 = all([settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, settings.AWS_S3_BUCKET])
        if self.use_s3:
            import boto3
            self.s3_client = boto3.client(
                "s3",
                region_name=settings.AWS_S3_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            self.bucket = settings.AWS_S3_BUCKET

    async def upload(self, file: UploadFile, folder: str = "uploads") -> str:
        ext = os.path.splitext(file.filename or "file")[1]
        key = f"{folder}/{uuid.uuid4()}{ext}"

        if self.use_s3:
            return await self._upload_s3(file, key)
        return await self._upload_local(file, key)

    async def _upload_s3(self, file: UploadFile, key: str) -> str:
        from botocore.exceptions import ClientError
        contents = await file.read()
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.put_object(
                    Bucket=self.bucket, Key=key, Body=contents, ContentType=file.content_type
                ),
            )
            base = settings.STORAGE_BASE_URL or f"https://{self.bucket}.s3.{settings.AWS_S3_REGION}.amazonaws.com"
            return f"{base}/{key}"
        except ClientError as e:
            raise RuntimeError(f"S3 upload failed: {e}") from e

    async def _upload_local(self, file: UploadFile, key: str) -> str:
        os.makedirs(os.path.dirname(key) or ".", exist_ok=True)
        file_path = os.path.join(os.getcwd(), key)
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        return f"/{key}"


storage_service = StorageService()
