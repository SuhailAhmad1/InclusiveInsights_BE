import os
import subprocess
import requests
from pdf2image import convert_from_path
import time
import json
from urllib.parse import urlparse
import boto3
from celery import shared_task
from config import TEMP_FILES_DIR
from app.crud.dashboard_crud import store_module_extraction_data, update_module_status

from config import AWS_ACCESS_KEY_ID, \
    AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, S3_BUCKET_NAME

def generate_thumbnail(file_content):
    timestamp = str(int(time.time()))
    temp_docx_path = f'{TEMP_FILES_DIR}{timestamp}-temp.docx'
    with open(temp_docx_path, 'wb') as temp_docx_file:
        temp_docx_file.write(file_content)
        
    pdf_path = temp_docx_path.replace('.docx', '.pdf')
    subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf','--outdir', TEMP_FILES_DIR, temp_docx_path], check=True)

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF conversion failed. File {pdf_path} not found.")

    try:
        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        thumbnail_path = temp_docx_path.replace('.docx', '_thumbnail.png')
        images[0].save(thumbnail_path, 'PNG') 
    except Exception as e:
        raise RuntimeError(f"Failed to generate thumbnail: {e}")

    os.remove(temp_docx_path)
    os.remove(pdf_path)

    return thumbnail_path


def generate_pre_signed_url(s3_path):
    parsed_url = urlparse(s3_path)
    bucket_name = parsed_url.netloc
    s3_key = parsed_url.path.lstrip('/')
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )

    presigned_url = s3_client.generate_presigned_url('get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': s3_key
                    },
                ExpiresIn=86400  # URL expiration time in seconds (3600 = 1 hour)
        )
    
    return presigned_url

@shared_task
def initiate_extraction_task(module_id, module_api, file_path, page_margins=None):
    try:
        request_body = {
            'file_path': file_path
        }

        if page_margins:
            request_body["margin_dict"] = page_margins

        print(request_body, module_api)
        start_time = time.time()
        response = requests.post(module_api, json=request_body, timeout=120)
        if response.status_code == 200:
            time_taken = time.time() - start_time
            store_module_extraction_data(module_id, json.dumps(response.json()["data"]), time_taken)
            # store_module_extraction_data(module_id, json.dumps(response.json()), time_taken)
            return "Success"                     
        else:
            print(module_api, response.json())
            update_module_status(module_id, "failed")
            return "Failure"
    
    except Exception as e:
        print(e)
        print(module_api)
        update_module_status(module_id, "failed")
        return "Something went wrong while calling DS API"