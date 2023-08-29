from fastapi import FastAPI
from src.auth.config import auth_backend, fastapi_users
from src.auth.schemas import UserRead, UserUpdate
from src.auth.config import google_oauth_client, facebook_oauth_client
from src.config.settings import SECRET_AUTH
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import DATABASE_URI, APPS_MODELS
from tortoise.contrib.fastapi import register_tortoise
from src.auth.router import router as router_verify
from src.file.router import router as file_router
from src.info.router import router as info_router
from src.pay.router import router as pay_router
from src.admin.router import router as admin_router
from fastapi_pagination import add_pagination
from src.auth.router import get_auth_router


app = FastAPI(
    title="Safecam"
)

add_pagination(app)

app.include_router(
    get_auth_router(backend = auth_backend, requires_verification=True),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(router_verify)

app.include_router(admin_router)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

app.include_router(
    fastapi_users.get_oauth_router(google_oauth_client, auth_backend, SECRET_AUTH, associate_by_email=True, is_verified_by_default=True),
    prefix="/auth/google",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_oauth_router(facebook_oauth_client, auth_backend, SECRET_AUTH),
    prefix="/auth/facebook",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_oauth_router(google_oauth_client, auth_backend, SECRET_AUTH),
    prefix="/auth/apple",
    tags=["auth"],
)

app.include_router(file_router)
app.include_router(info_router)
app.include_router(pay_router)


origins = ['*']
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)


register_tortoise(
    app,
    db_url=DATABASE_URI,
    modules={"models": APPS_MODELS},
    generate_schemas=True,
    add_exception_handlers=True,
)