from tortoise import Tortoise, run_async
from src.config.settings import APPS_MODELS, DATABASE_URI
from src.auth.models import User
from fastapi_users.password import PasswordHelper

async def main():
    """ Создание супер юзера
    """
    await Tortoise.init(
        db_url=DATABASE_URI,
        modules={"models": APPS_MODELS},
    )
    password_helper = PasswordHelper()
    print("Create superuser")
    name = input("Username: ")
    email = input("Email: ")
    password = input("Password: ")
    await User.create(name=name, email=email, hashed_password=password_helper.hash(password), is_superuser=True, is_verified=True, is_active=True)
    print("success")


if __name__ == '__main__':
    run_async(main())
