import os
from dotenv import load_dotenv

load_dotenv()
import json

APP_HOST = os.getenv("APP_HOST")
APP_PORT = int(os.getenv("APP_PORT"))

DB_URI = os.getenv("DB_URI")

ALGORITHM = os.getenv('ALGORITHM')
SECRET_KEY = os.getenv('SECRET_KEY')
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv('ACCESS_TOKEN_EXPIRE_DAYS'))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS'))

DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR")
STATIC_DIR = os.getenv("STATIC_DIR")