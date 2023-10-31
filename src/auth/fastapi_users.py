from fastapi_users import FastAPIUsers
from .manager import get_user_manager
from .auth import auth_backend
from db import User


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)
