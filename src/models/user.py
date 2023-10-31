
from sqlalchemy import Table, Column, Integer, String, Boolean, Float
from db.config import metadata


user = Table(
    'user', 
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('username', String, unique=True, nullable=False),
    Column('hashed_password', String, nullable=False),
    Column('is_superuser', Boolean, nullable=False, default=False),
    Column('balance', Float, default=0.00, nullable=False),
    Column('is_active', Boolean, default=True, nullable=False),
    Column('email', String, nullable=True),
    Column('is_verified', Boolean, default=True, nullable=False),
)

