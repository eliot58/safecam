from enum import Enum
from fastapi_mail import FastMail, MessageSchema
from fastapi_users_tortoise import TortoiseUserDatabase
from src.auth.models import OAuthAccount, User
from src.config.settings import EmailConfig
from fastapi_users.exceptions import FastAPIUsersException

class MyErrorCode(str, Enum):
    REGISTER_PHONE_ALREADY_EXISTS = "REGISTER_PHONE_ALREADY_EXISTS"
    LOGIN_IS_NOT_ACTIVE = "LOGIN_IS_NOT_ACTIVE"

class PhoneAlreadyExists(FastAPIUsersException):
    pass

class MyTortoiseUserDatabase(TortoiseUserDatabase):
    async def get_by_phone(self, phone: str):
        query = self.user_model.filter(phone=phone).first()

        return await query


async def get_user_db():
    yield MyTortoiseUserDatabase(User, OAuthAccount)


async def send_pin(email, otp):
    fm = FastMail(EmailConfig)
    template = f"""
        <html>
        <body>
         
 
        <p>Hi !!! <br>OTP {otp}</p>
 
 
        </body>
        </html>
    """

    message = MessageSchema(
        subject="OTP",
        recipients=[email],
        body=template,
        subtype="html"
    )

    await fm.send_message(message=message)