
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from typing import AsyncGenerator
from fastapi import Depends
from .user import User
from .config import *


DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
async_engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def get_all_users():
    async with async_session_maker() as session:
        query = select(User)
        result = await session.execute(query)
        users = result.scalars().all()
        return users


async def check_username(username: str):
    async with async_session_maker() as session:
        query = select(User).where(User.username == username)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        return user


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


