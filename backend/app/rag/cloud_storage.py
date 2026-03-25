import boto3
from botocore.client import Config
from app.core.config import settings
import os

class R2Storage:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=f'https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
            aws_access_key_id=settings.R2_ACCESS_KEY,
            aws_secret_access_key=settings.R2_SECRET_KEY,
            config=Config(signature_version='s3v4'),
            region_name='auto'  # Cloudflare R2 ignores region but boto3 requires it
        )
        self.bucket_name = settings.R2_BUCKET_NAME

    def upload_file(self, file_path, object_name=None):
        """Upload a file to an R2 bucket"""
        if object_name is None:
            object_name = os.path.basename(file_path)

        try:
            self.s3.upload_file(file_path, self.bucket_name, object_name)
            return True
        except Exception as e:
            print(f"Error uploading to R2: {e}")
            return False

    def upload_fileobj(self, file_obj, object_name):
        """Upload a file object to an R2 bucket"""
        try:
            self.s3.upload_fileobj(file_obj, self.bucket_name, object_name)
            return True
        except Exception as e:
            print(f"Error uploading to R2: {e}")
            return False

    def generate_presigned_url(self, object_name, expiration=3600):
        """Generate a URL to share an R2 object. Uses custom domain if available."""
        if settings.R2_CUSTOM_DOMAIN:
            # If using a custom domain, we assume it's publicly accessible or handled via Workers
            # Strip trailing slash if present
            base_url = settings.R2_CUSTOM_DOMAIN.rstrip('/')
            return f"{base_url}/{object_name}"
            
        try:
            response = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            return response
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return None

    def list_files(self, prefix=''):
        """List files in the R2 bucket"""
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except Exception as e:
            print(f"Error listing R2 files: {e}")
            return []

    def delete_file(self, object_name):
        """Delete a file from the R2 bucket"""
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except Exception as e:
            print(f"Error deleting from R2: {e}")
            return False

r2_storage = R2Storage()
