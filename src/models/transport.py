
from sqlalchemy import Table, Column, Integer, String, Boolean, Float, ForeignKey
from db.config import metadata
from .user import user


transport = Table(
    'transport',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('owner_id', Integer, ForeignKey(user.c.id, ondelete='CASCADE',onupdate='CASCADE'), nullable=False),
    Column('can_be_rented', Boolean, nullable=False, default=True),
    Column('transport_type', String, nullable=False),
    Column('model', String, nullable=False),
    Column('color', String, nullable=False),
    Column('identifier', String, nullable=False),
    Column('description', String, nullable=True),
    Column('latitude', Float, nullable=False),
    Column('longitude', Float, nullable=False),
    Column('minute_price', Float, nullable=True),
    Column('day_price', Float, nullable=True),
)

