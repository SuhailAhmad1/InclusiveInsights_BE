from botocore.exceptions import BotoCoreError, ClientError
import asyncio
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

from app.core.s3 import s3_client
from config import (
    S3_BUCKET_NAME,
    S3_EXCECUTOR_WORKERS,
    S3_URL_EXPIREY
)

s3_executor = ThreadPoolExecutor(max_workers=S3_EXCECUTOR_WORKERS)


async def upload_file_to_s3(file, key) -> str:
    """
    Uploads a file object to S3 and returns the file URL.
    """
    def _upload():
        s3_client.upload_fileobj(
            Fileobj=file.file,
            Bucket=S3_BUCKET_NAME,
            Key=key
        )

        head_response = s3_client.head_object(
            Bucket=S3_BUCKET_NAME,
            Key=key
        )
        return {
            "version_id": head_response.get("VersionId", None),
            "file_size": head_response.get("ContentLength")
        }

    try:
        return await asyncio.get_event_loop().run_in_executor(s3_executor, _upload)
    except (ClientError, BotoCoreError) as e:
        raise e
    except Exception as e:
        raise e


def generate_pre_signed_url(s3_key, version_id=None, is_pdf=False):
    try:
        if is_pdf:
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': S3_BUCKET_NAME,
                    'Key': s3_key,
                    'VersionId': version_id,
                    'ResponseContentType': 'application/pdf'
                },
                # URL expiration time in seconds (3600 = 1 hour)
                ExpiresIn=S3_URL_EXPIREY
            )
        else:
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': S3_BUCKET_NAME,
                    'Key': s3_key
                },
                # URL expiration time in seconds (3600 = 1 hour)
                ExpiresIn=S3_URL_EXPIREY
            )

        return presigned_url

    except (ClientError, BotoCoreError) as e:
        raise e
    except Exception as e:
        raise e