
from fastapi import APIRouter, Depends, HTTPException
from fastapi_users.password import PasswordHelper
from db import async_session_maker, User
from sqlalchemy.future import select
from schemas import UserCreateAdmin
from sqlalchemy import delete
from auth import fastapi_users


admin_account_controller = APIRouter()
password_helper = PasswordHelper()
current_superuser = fastapi_users.current_user(active=True, superuser=True)


@admin_account_controller.get("/")
async def get_all_users(
    start: int = 0,
    count: int = 10,
    user: User = Depends(current_superuser),
):
    async with async_session_maker() as session:
        async with session.begin():
            stmt = select(User).offset(start).limit(count)
            result = await session.execute(stmt)
            users = result.scalars().all()
            
            if users == None:
                raise HTTPException(status_code=404, detail="No users found")

            return users


@admin_account_controller.get("/{id}")
async def get_user_by_id(id: int ,user: User = Depends(current_superuser)):
    async with async_session_maker() as session:
        async with session.begin():
            stmt = select(User).where(User.id == id)
            result = await session.execute(stmt)
            user = result.scalars().first()

            if user == None:
                raise HTTPException(status_code=404, detail="User not found")

            return user


@admin_account_controller.post("/")
async def create_user(user: UserCreateAdmin, current_user: User = Depends(current_superuser)):
    async with async_session_maker() as session:
        async with session.begin():
            stmt = select(User).where(User.username == user.username)
            result = await session.execute(stmt)
            existing_user = result.scalars().first()

            if existing_user:
                raise HTTPException(status_code=400, detail="User already exists")

            new_user = User(
                username=user.username,
                email=user.username + "@mail.com",
                hashed_password=password_helper.hash(user.password),
                is_superuser=user.isAdmin,
                balance=user.balance
            )

            session.add(new_user)

            await session.commit()
            return new_user


@admin_account_controller.put("/{id}")
async def update_user(id: int, user: UserCreateAdmin, current_user: User = Depends(current_superuser)):
    async with async_session_maker() as session:
        async with session.begin():
            stmt = select(User).where(User.id == id)
            result = await session.execute(stmt)
            existing_user = result.scalars().first()

            if existing_user:
                if user.username != existing_user and user.username != None:
                    query = select(User).where(User.username == user.username)
                    result = await session.execute(query)
                    ex_user = result.scalar_one_or_none()

                    if ex_user:
                        raise HTTPException(status_code=400, detail="User already exists")
                    else:
                        existing_user.username = user.username
                        existing_user.email = user.username + "@mail.com"


                existing_user.hashed_password = password_helper.hash(user.password)
                existing_user.is_superuser = user.isAdmin
                existing_user.balance = user.balance

                await session.commit()
                return existing_user

            else:
                raise HTTPException(status_code=404, detail="User not found")


@admin_account_controller.delete("/{id}")
async def delete_user(id: int, current_user: User = Depends(current_superuser)):
    async with async_session_maker() as session:
        async with session.begin():
            stmt = select(User).where(User.id == id)
            result = await session.execute(stmt)
            existing_user = result.scalars().first()

            if existing_user:
                query = (
                    delete(User)
                    .where(User.id == id)
                )
                await session.execute(query)

                await session.commit()
                raise HTTPException(status_code=200, detail="User deleted")

            else:
                raise HTTPException(status_code=404, detail="User not found")

