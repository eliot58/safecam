import os

from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig

load_dotenv()

DATABASE_URI = f'postgres://{os.environ.get("DB_USER")}:' \
               f'{os.environ.get("DB_PASS")}@' \
               f'{os.environ.get("DB_HOST")}:5432/' \
               f'{os.environ.get("DB_NAME")}'

GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
FACEBOOK_OAUTH_CLIENT_ID = os.environ.get("FACEBOOK_OAUTH_CLIENT_ID")
FACEBOOK_OAUTH_CLIENT_SECRET = os.environ.get("FACEBOOK_OAUTH_CLIENT_SECRET")
APPLE_OAUTH_CLIENT_ID = os.environ.get("APPLE_OAUTH_CLIENT_ID")
APPLE_OAUTH_CLIENT_SECRET = os.environ.get("APPLE_OAUTH_CLIENT_SECRET")

# DB_HOST_TEST = os.environ.get("DB_HOST_TEST")
# DB_PORT_TEST = os.environ.get("DB_PORT_TEST")
# DB_NAME_TEST = os.environ.get("DB_NAME_TEST")
# DB_USER_TEST = os.environ.get("DB_USER_TEST")
# DB_PASS_TEST = os.environ.get("DB_PASS_TEST")

BROKER = os.environ.get("BROKER")

SECRET_AUTH = os.environ.get("SECRET_AUTH")

SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

EmailConfig = ConnectionConfig(
   MAIL_USERNAME=SMTP_USER,
   MAIL_PASSWORD=SMTP_PASSWORD,
   MAIL_FROM = SMTP_USER,
   MAIL_PORT=465,
   MAIL_SERVER="smtp.gmail.com",
   MAIL_STARTTLS = False,
   MAIL_SSL_TLS = True,
   USE_CREDENTIALS = True,
   VALIDATE_CERTS = True
)


aws_access_key_id = os.environ.get("aws_access_key_id")
aws_secret_access_key = os.environ.get("aws_secret_access_key")

bucket = {"Name": "4696025b-1f120c52-ef58-4db6-9fd8-03a75baf6f48"}

APPS_MODELS = [
    "src.auth.models",
    "src.file.models",
    "src.info.models",
    "src.pay.models",
    "aerich.models",
]


GOOGLE_MAP = os.environ.get("GOOGLE_MAP")