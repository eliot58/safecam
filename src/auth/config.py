from fastapi_users.authentication import BearerTransport
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users import FastAPIUsers
from src.auth.manager import get_user_manager
from src.config.settings import SECRET_AUTH, GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET, FACEBOOK_OAUTH_CLIENT_ID, FACEBOOK_OAUTH_CLIENT_SECRET, APPLE_OAUTH_CLIENT_ID, APPLE_OAUTH_CLIENT_SECRET
from src.auth.models import User
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.facebook import FacebookOAuth2
from httpx_oauth.oauth2 import OAuth2

google_oauth_client = GoogleOAuth2(
    GOOGLE_OAUTH_CLIENT_ID,
    GOOGLE_OAUTH_CLIENT_SECRET
)

facebook_oauth_client = FacebookOAuth2(
    FACEBOOK_OAUTH_CLIENT_ID,
    FACEBOOK_OAUTH_CLIENT_SECRET
)

# apple_oauth_client = OAuth2(
#     APPLE_OAUTH_CLIENT_ID,
#     APPLE_OAUTH_CLIENT_SECRET,

# )

bearer_transport = BearerTransport(tokenUrl="auth/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET_AUTH, lifetime_seconds=3600 * 24 * 30)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend]
)

current_user = fastapi_users.current_user(active=True, verified=True)