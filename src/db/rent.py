
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Float
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from models import user, transport
from datetime import datetime


Base: DeclarativeMeta = declarative_base()


class Rent(Base):
    __tablename__ = 'rent'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(user.c.id, ondelete='CASCADE',onupdate='CASCADE'))
    transport_id = Column(Integer, ForeignKey(transport.c.id, ondelete='CASCADE',onupdate='CASCADE'))
    rent_type = Column(String, nullable=False)
    start_rent = Column(TIMESTAMP, nullable=False, default=datetime.strptime(datetime.utcnow().replace(microsecond=0).isoformat(), "%Y-%m-%dT%H:%M:%S"))
    end_rent = Column(TIMESTAMP, nullable=True)
    rent_price = Column(Float, nullable=False)
    final_price = Column(Float, nullable=True)
    

