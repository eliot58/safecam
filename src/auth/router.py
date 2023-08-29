from datetime import datetime, timedelta
from random import randint
from fastapi import APIRouter, HTTPException, Depends, HTTPException, Request, status
from pydantic import EmailStr
from src.auth.manager import UserManager, get_user_manager
from src.auth.schemas import UserRead, Verify, UserCreate, Reset
from src.auth.utils import send_pin
from src.auth.models import User
from fastapi_users.router.common import ErrorModel, ErrorCode
from src.auth.utils import MyErrorCode
from fastapi_users import exceptions
from src.auth.utils import PhoneAlreadyExists
from fastapi_users.password import PasswordHelper
import pytz
from src.info.models import UserStatistic
from tortoise.exceptions import DoesNotExist
from src.auth.config import current_user, auth_backend
from fastapi_users.authentication import AuthenticationBackend, Authenticator, Strategy
from fastapi_users.manager import BaseUserManager, UserManagerDependency
from fastapi_users.openapi import OpenAPIResponseType
from typing import Tuple, Sequence
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import models
from fastapi_users.router.common import ErrorCode, ErrorModel

router = APIRouter(
    tags=["auth"]
)

@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    name="register:register",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                            "summary": "A user with this email already exists.",
                            "value": {
                                "detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS
                            },
                        },
                        MyErrorCode.REGISTER_PHONE_ALREADY_EXISTS: {
                            "summary": "A user with this phone already exists.",
                            "value": {
                                "detail": MyErrorCode.REGISTER_PHONE_ALREADY_EXISTS
                            },
                        },
                        ErrorCode.REGISTER_INVALID_PASSWORD: {
                            "summary": "Password validation failed.",
                            "value": {
                                "detail": {
                                    "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                                    "reason": "Password should be"
                                    "at least 8 characters",
                                }
                            },
                        },
                    }
                }
            },
        },
    },
)
async def register(
    request: Request,
    user_create: UserCreate,
    user_manager: UserManager = Depends(get_user_manager),
):
    try:
        created_user = await user_manager.create(
            user_create, safe=True, request=request
        )
    except exceptions.UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )
    except PhoneAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=MyErrorCode.REGISTER_PHONE_ALREADY_EXISTS,
        )
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )
    
    try:
        user_stats = await UserStatistic.get(date=datetime.utcnow().date().strftime("%Y-%m-%d"))
    except DoesNotExist:
        all_user_stats = await UserStatistic.all()
        if len(all_user_stats) == 0:
            await UserStatistic.create(users=1, new_subscribed = 0, cancel_subscribed = 0, date=datetime.utcnow().date())
        else:
            await UserStatistic.create(users=all_user_stats[-1].users + 1, new_subscribed = all_user_stats[-1].new_subscribed, cancel_subscribed = all_user_stats[-1].cancel_subscribed,  date=datetime.utcnow().date())
    else:
        user_stats.users = user_stats.users + 1
        await user_stats.save()

    


    return UserRead.from_orm(created_user)

@router.post("/request-verify")
async def request_verify(email: EmailStr):
    try:
        otp = randint(1000, 9999)
        await User.filter(email = email).update(otp = otp, date_of_send_otp=datetime.now())
        await send_pin(email, otp)
    except Exception:
        raise HTTPException(400, detail="Bad request")
    return {"status": "success", "detail": "pin send", "data": None}

@router.post("/verify")
async def verify(verify_data: Verify):
    user = await User.filter(email = verify_data.email).first()
    if user.date_of_send_otp.replace(tzinfo=pytz.UTC) + timedelta(minutes=3) < datetime.utcnow().replace(tzinfo=pytz.UTC):
        raise HTTPException(400, detail="Pin code expired")
    if user.otp != verify_data.otp:
        raise HTTPException(400, detail="Lol")
    user.is_verified = True
    await user.save()
    return {"status": "success", "detail": "verified", "data": None}


@router.post("/forgot-password")
async def forgot(email: EmailStr):
    try:
        otp = randint(1000, 9999)
        await User.filter(email = email).update(otp = otp, date_of_send_otp=datetime.now())
        await send_pin(email, otp)
    except Exception:
        raise HTTPException(400, detail="Bad request")
    return {"status": "success", "detail": "pin send", "data": None}

@router.post("/reset-password")
async def reset(reset_data: Reset):
    user = await User.filter(email = reset_data.email).first()
    if user.date_of_send_otp.replace(tzinfo=pytz.UTC) + timedelta(minutes=3) < datetime.utcnow().replace(tzinfo=pytz.UTC):
        raise HTTPException(400, detail="Pin code expired")
    if user.otp != reset_data.otp:
        raise HTTPException(400, detail="Lol")
    password_helper = PasswordHelper()
    user.hashed_password = password_helper.hash(reset_data.new_password)
    await user.save()
    return {"status": "success", "detail": "password recovered", "data": None}

@router.get("/my-tarif")
async def my_tarif(user: User = Depends(current_user)):
    return await user.tarif


def auth_router(
    backend: AuthenticationBackend,
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    authenticator: Authenticator,
    requires_verification: bool = False,
) -> APIRouter:
    """Generate a router with login/logout routes for an authentication backend."""
    router = APIRouter()
    get_current_user_token = authenticator.current_user_token(
        active=True, verified=requires_verification
    )

    login_responses: OpenAPIResponseType = {
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.LOGIN_BAD_CREDENTIALS: {
                            "summary": "Bad credentials or the user is inactive.",
                            "value": {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS},
                        },
                        ErrorCode.LOGIN_USER_NOT_VERIFIED: {
                            "summary": "The user is not verified.",
                            "value": {"detail": ErrorCode.LOGIN_USER_NOT_VERIFIED},
                        },
                    }
                }
            },
        },
        **backend.transport.get_openapi_login_responses_success(),
    }

    @router.post(
        "/login",
        name=f"auth:{backend.name}.login",
        responses=login_responses,
    )
    async def login(
        request: Request,
        credentials: OAuth2PasswordRequestForm = Depends(),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
    ):
        user = await user_manager.authenticate(credentials)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=MyErrorCode.LOGIN_IS_NOT_ACTIVE,
            )
        if requires_verification and not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_USER_NOT_VERIFIED,
            )
        response = await backend.login(strategy, user)
        await user_manager.on_after_login(user, request, response)
        return response

    logout_responses: OpenAPIResponseType = {
        **{
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token or inactive user."
            }
        },
        **backend.transport.get_openapi_logout_responses_success(),
    }

    @router.post(
        "/logout", name=f"auth:{backend.name}.logout", responses=logout_responses
    )
    async def logout(
        user_token: Tuple[models.UP, str] = Depends(get_current_user_token),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
    ):
        user, token = user_token
        return await backend.logout(strategy, user, token)

    return router


def get_auth_router(backend: AuthenticationBackend, requires_verification: bool = False
    ) -> APIRouter:
        """
        Return an auth router for a given authentication backend.

        :param backend: The authentication backend instance.
        :param requires_verification: Whether the authentication
        require the user to be verified or not. Defaults to False.
        """
        return auth_router(
            backend,
            get_user_manager,
            Authenticator([auth_backend], get_user_manager),
            requires_verification,
        )


@router.post("/unlock")
async def unlock(email: EmailStr):
    user = await User.get(email=email)
    user.is_unlock = True
    await user.save()
    return {"status": "success", "detail": "send"}