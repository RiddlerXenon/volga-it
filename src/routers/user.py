
from fastapi import APIRouter, Depends, HTTPException, Request, status
from auth import auth_backend, fastapi_users, get_user_manager
from fastapi_users.router.common import ErrorCode, ErrorModel
from fastapi_users import models, schemas, exceptions
from fastapi_users.openapi import OpenAPIResponseType
from schemas import UserRead, UserCreate, UserSignIn
from fastapi_users.authentication import Strategy
from fastapi_users.manager import BaseUserManager
from db import User, async_session_maker
from sqlalchemy.future import select
from sqlalchemy import update
from typing import Tuple


account_controller = APIRouter()
current_user = fastapi_users.current_user(active=True)


@account_controller.get("/Me", tags=["AccountController"])
async def me(user: User = Depends(current_user)):
    return user


backend = auth_backend
get_user_manager = fastapi_users.get_user_manager
authenticator = fastapi_users.authenticator
requires_verification = False
get_current_user_token = authenticator.current_user_token(active=True, verified=requires_verification)

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

login_schema = UserSignIn


@account_controller.post("/SingIn",name=f"auth:{backend.name}.login",responses=login_responses)
async def login(
    request: Request,
    credentials: login_schema,
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
):
    user = await user_manager.authenticate(credentials)
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
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

@account_controller.post("/SignOut", name=f"auth:{backend.name}.logout", responses=logout_responses)
async def logout(
    user_token: Tuple[models.UP, str] = Depends(get_current_user_token),
    strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
):
    user, token = user_token
    return await backend.logout(strategy, user, token)


user_schema = UserRead
user_create_schema = UserCreate
 

@account_controller.post(
    "/SingUp",
    response_model=user_schema,
    status_code=status.HTTP_201_CREATED,
    name="register:register",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                            "summary": "A user with this username already exists.",
                            "value": {
                                "detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS
                            },
                        },
                        ErrorCode.REGISTER_INVALID_PASSWORD: {
                            "summary": "Password validation failed.",
                            "value": {
                                "detail": {
                                    "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                                    "reason": "Password should be"
                                    "at least 3 characters",
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
    user_create: user_create_schema,
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
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
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )

    return schemas.model_validate(user_schema, created_user)


user_update_schema = UserCreate


@account_controller.put("/Update", name="account:update")
async def update_user(
    user_update: user_update_schema,
    user: User = Depends(current_user),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),

):
    if user_update.username != None and user_update.password != None:
        async with async_session_maker() as session:
            if user_update.username != user.username:
                query = select(User).where(User.username == user_update.username)
                result = await session.execute(query)
                existing_user = result.scalar_one_or_none()

                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
                    )

            query = (
                update(User)
                .where(User.id == user.id)
                .values(
                    username=user_update.username, 
                    hashed_password=user_manager.password_helper.hash(user_update.password),
                    email=user_update.username + "@mail.com"
                )
            )
            await session.execute(query)
            await session.commit()
            
    raise HTTPException(status_code=200, detail="User updated")

