from datetime import datetime
from random import randint
from fastapi import Depends, Request
from typing import Optional
from fastapi_users import BaseUserManager, IntegerIDMixin
from src.config.settings import SECRET_AUTH
from src.auth.models import User
from src.auth.utils import MyTortoiseUserDatabase, get_user_db, send_pin
from fastapi_users import exceptions, schemas, models
from src.auth.utils import PhoneAlreadyExists
from fastapi_users import exceptions

class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET_AUTH
    verification_token_secret = SECRET_AUTH

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        
        if len(user_create.password) < 8:
            raise exceptions.InvalidPasswordException("Password should be at least 8 characters")

        
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()
        
        existing_phone = await self.user_db.get_by_phone(user_create.phone)
        if existing_phone is not None:
            raise PhoneAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user
    
    async def on_after_register(self, user: User, request: Request | None = None):
        otp = randint(1000, 9999)
        await User.filter(email = user.email).update(otp = otp, date_of_send_otp=datetime.now())
        await send_pin(user.email, otp)

async def get_user_manager(user_db: MyTortoiseUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)