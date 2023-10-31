
from .database import get_user_db, check_username, async_engine, async_session_maker
from .transport import Transport
from .user import User
from .rent import Rent

from sqlalchemy import create_engine
from fastapi_users.password import PasswordHelper
from .config import *
from models import *


password_helper = PasswordHelper()
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")


def drop_tables() -> None:
    metadata.drop_all(engine)


def create_tables() -> None:
    metadata.create_all(engine)


def fill_tables() -> None:
    conn = engine.connect()
    
    conn.execute(user.insert(), [
        {
            'username': 'user1',
            'email': 'user1@mail.com',
            'hashed_password': password_helper.hash('password1'),
            'is_superuser': True,
        },
        {
            'username': 'user2',
            'email': 'user2@mail.com',
            'hashed_password': password_helper.hash('password2'),
            'is_superuser': False,
        },
        {
            'username': 'user3',
            'email': 'user3@mail.com',
            'hashed_password':password_helper.hash('password3'),
            'is_superuser': False,
        },
        {
            'username': 'fastapiusersauth',
            'email': 'fastapiusersauth@mail.com',
            'hashed_password': password_helper.hash('fastapiusersauth'),
            'is_superuser': True,
        },
    ])

    conn.execute(transport.insert(), [
        {
            'owner_id': 1,
            'transport_type': 'car',
            'model': 'BMW',
            'color': 'black',
            'identifier': 'AA1234AA',
            'latitude': 55.7558,
            'longitude': 37.6173,
            'minute_price': 10,
            'day_price': 100,
        },
        {
            'owner_id': 2,
            'can_be_rented': False,
            'transport_type': 'bike',
            'model': 'BMX',
            'color': 'red',
            'identifier': 'BB1234BB',
            'latitude': 55.7558,
            'longitude': 37.6173,
            'minute_price': 5,
            'day_price': 50,
        },
    ])

    conn.execute(rent.insert(), [
        {
            'user_id': 3,
            'transport_id': 1,
            'rent_type': 'minute',
            'rent_price': 10,
        },
        {
            'user_id': 3,
            'transport_id': 2,
            'rent_type': 'day',
            'rent_price': 50,
        },
        {
            'user_id': 2,
            'transport_id': 1,
            'rent_type': 'minute',
            'start_time': '2021-01-01T00:00:00',
            'end_time': '2021-01-01T00:01:00',
            'rent_price': 10,
            'final_price': 100,
        },
    ])
    
    conn.commit()
    conn.close()

