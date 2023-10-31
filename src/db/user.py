
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float
from fastapi_users.db import SQLAlchemyBaseUserTable


Base: DeclarativeMeta = declarative_base()


class User(SQLAlchemyBaseUserTable[int], Base):
    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String, unique=True, nullable=False)
    hashed_password: str = Column(String, nullable=False)
    is_superuser: bool = Column(Boolean, nullable=False, default=False)
    balance: float = Column(Float, nullable=False, default=0.00)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    email: str = Column(String, nullable=True)
    is_verified: bool = Column(Boolean, default=True, nullable=False)

