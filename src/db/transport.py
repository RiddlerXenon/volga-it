
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from models import user


Base: DeclarativeMeta = declarative_base()


class Transport(Base):
    __tablename__ = 'transport'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey(user.c.id, ondelete='CASCADE',onupdate='CASCADE'), nullable=False)
    can_be_rented = Column(Boolean, nullable=False, default=True)
    transport_type = Column(String, nullable=False)
    model = Column(String, nullable=False)
    color = Column(String, nullable=False)
    identifier = Column(String, nullable=False)
    description = Column(String, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    minute_price = Column(Float, nullable=True)
    day_price = Column(Float, nullable=True)
    

