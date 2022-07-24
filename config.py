import os
from dotenv import load_dotenv

load_dotenv()

class Config(object):
    DATABASE = os.environ.get('DATABASE')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    MAIL_ASCII_ATTACHMENTS = True
