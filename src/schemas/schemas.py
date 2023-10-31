
from fastapi_users import schemas
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRead(schemas.BaseUser[int]):
    id: int
    email: str
    username: str
    balance: float
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


    class Config:
        from_atrributes = ["id", "email", "username", "balance", "is_active", "is_superuser", "is_verified"]


class UserCreate(schemas.CreateUpdateDictModel):
    username: str
    password: str


class UserCreateAdmin(BaseModel):
    username: str
    password: str
    isAdmin: Optional[bool] = False
    balance: Optional[float] = 0.00


class UserSignIn(BaseModel):
    username: str
    password: str


class TransportType(Enum):
    car = "car"
    bike = "bike"
    scooter = "scooter"
    all = "all"


class TransportCreate(BaseModel):
    canBeRented: bool
    transportType: TransportType
    model: str
    color: str
    identifier: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    minutePrice: Optional[float] = None
    dayPrice: Optional[float] = None


class TransportCreateAdmin(BaseModel):
    ownerId: int
    canBeRented: bool
    transportType: TransportType
    model: str
    color: str
    identifier: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    minutePrice: Optional[float] = None
    dayPrice: Optional[float] = None


class RentType(Enum):
    minute = "minute"
    day = "day"


class RentCreate(BaseModel):
    rent_type: RentType


class RentCreateAdmin(BaseModel):
    transportId: int
    userId: int
    timeStart: str
    timeEnd: Optional[str] = None
    priceOfUnit: float
    priceType: RentType
    finalPrice: Optional[float] = None

