import phonenumbers
from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional
from src.auth.models import Status

class UserRead(schemas.BaseUser[int]):
    phone: Optional[str]
    name: Optional[str]
    registered_at: datetime
    status: Optional[Status]
    auto_upload: bool



class UserUpdate(schemas.BaseUserUpdate):
    auto_upload: Optional[bool]


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str
    phone: str
    name: str

    @validator("phone")
    def phone_validation(cls, v):

        try:
            pn = phonenumbers.parse(v)
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValueError('Invalid phone number format')

        return v
    
    
class Verify(BaseModel):
    otp: int
    email: EmailStr


class Reset(BaseModel):
    otp: int
    email: EmailStr
    new_password: str