
from sqlalchemy import Table, Column, Integer, String, ForeignKey, TIMESTAMP, Float
from .transport import transport
from datetime import datetime
from db.config import metadata
from .user import user


rent = Table(
    'rent',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey(user.c.id, ondelete='CASCADE',onupdate='CASCADE')),
    Column('transport_id', Integer, ForeignKey(transport.c.id, ondelete='CASCADE',onupdate='CASCADE')),
    Column('rent_type', String, nullable=False),
    Column('start_rent', TIMESTAMP, nullable=False, default=datetime.utcnow().replace(microsecond=0).isoformat()),
    Column('end_rent', TIMESTAMP, nullable=True),
    Column('rent_price', Float, nullable=False),
    Column('final_price', Float, nullable=True)
)

