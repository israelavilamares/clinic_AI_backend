import os
from fastapi_mail import fastmail,  MessageSchema, ConnectionConfig
import secrets

from dotenv import load_dotenv
load_dotenv()
conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    MAIL_PORT = os.getenv("MAIL_PORT"), 
    MAIL_DEBUG= 0,
    MAIL_SERVER = os.getenv("MAIL_SERVER"),
    MAIL_TLS = os.getenv("MAIL_TLS"),
    MAIL_SSL=False,
    USE_CREDENTIALS=True
)


def generate_token():
    return secrets.token_urlsafe(32)