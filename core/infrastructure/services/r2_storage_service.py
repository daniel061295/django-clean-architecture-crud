import logging
from typing import Optional
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from django.conf import settings

from core.domain.services import StorageServiceInterface


logger = logging.getLogger(__name__)


class CloudflareR2StorageService(StorageServiceInterface):
    """
    Cloudflare R2 implementation of the StorageServiceInterface.
    Utilizes the boto3 S3 client configured for R2 endpoints.
    """

    def __init__(self) -> None:
        self.bucket_name = getattr(settings, "CLOUD_FLARE_R2_BUCKET_NAME", "")
        account_id = getattr(settings, "CLOUD_FLARE_ACCOUNT_ID", "")
        access_key = getattr(settings, "CLOUD_FLARE_ACCESS_KEY_ID", "")
        secret_key = getattr(settings, "CLOUD_FLARE_SECRET_ACCESS_KEY", "")

        # Initialize boto3 client for Cloudflare R2 with explicit v4 signature
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name="auto",  # R2 commonly accepts 'auto' or 'us-east-1'
            config=Config(signature_version="s3v4"),
        )

    def upload_file(self, file_data: bytes, file_name: str, content_type: str) -> str:
        """Uploads the file bytes to Cloudflare R2."""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=file_data,
                ContentType=content_type,
            )
            logger.info(f"Successfully uploaded file to R2: {file_name}")
            return file_name
        except ClientError as e:
            logger.error(f"Failed to upload file {file_name} to R2: {e}")
            raise ValueError(f"Storage Error: Could not upload file: {str(e)}")

    def delete_file(self, file_identifier: str) -> bool:
        """Deletes object from Cloudflare R2."""
        if not file_identifier:
            return False
            
        if file_identifier == "avatars/default.jpg":
            logger.info("Skipped deletion of protected default avatar.")
            return True
            
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_identifier
            )
            logger.info(f"Successfully deleted file from R2: {file_identifier}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file {file_identifier} from R2: {e}")
            return False

    def get_signed_url(self, file_identifier: str, expires_in_seconds: int = 3600) -> Optional[str]:
        """Generates a temporary presigned URL for secure frontend access."""
        if not file_identifier:
            return None
            
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": file_identifier},
                ExpiresIn=expires_in_seconds,
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate signed URL for {file_identifier}: {e}")
            return None
