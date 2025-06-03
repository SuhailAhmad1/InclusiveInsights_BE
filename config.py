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
USER_SIGNUP_KEY = os.getenv("USER_SIGNUP_KEY")

DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR")
STATIC_DIR = os.getenv("STATIC_DIR")


SENDER_EMAIL = os.getenv("APP_EMAIL")
EMAIL_PASSWORD = os.getenv("PASS_KEY")
WEBAPP_BASE_URL = os.getenv("WEBAPP_BASE_URL")