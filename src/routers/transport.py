
from db import User, async_session_maker, Transport
from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from schemas import TransportCreate
from fastapi import HTTPException
from auth import fastapi_users


transport_controller = APIRouter()
current_user = fastapi_users.current_user(active=True)


@transport_controller.get("/{id}")
async def get_transport(id: int):
    async with async_session_maker() as session:
        async with session.begin():
            stmt = select(Transport).where(Transport.id == id)
            result = await session.execute(stmt)
            transport = result.scalars().first()

            if transport == None:
                raise HTTPException(status_code=404, detail="Transport not found")

            return transport


@transport_controller.post("/")
async def create_transport(transport: TransportCreate, user: User = Depends(current_user)):
    async with async_session_maker() as session:
        async with session.begin():
            new_transport = Transport(**transport.dict(), owner_id=user.id)
            session.add(new_transport)
            await session.commit()
            return new_transport


@transport_controller.put("/{id}")
async def update_transport(id: int, transport: TransportCreate, user: User = Depends(current_user)):
    async with async_session_maker() as session:
        async with session.begin():
            stmt = select(Transport).where(Transport.id == id)
            result = await session.execute(stmt)
            existing_transport = result.scalars().first()
            
            if existing_transport == None:
                raise HTTPException(status_code=404, detail="Transport not found")

            if existing_transport.owner_id != user.id:
                raise HTTPException(status_code=403, detail="You are not the owner of this transport")

            existing_transport.can_be_rented = transport.canBeRented
            existing_transport.transport_type = transport.transportType
            existing_transport.model = transport.model
            existing_transport.color = transport.color
            existing_transport.identifier = transport.identifier
            existing_transport.description = transport.description
            existing_transport.latitude = transport.latitude
            existing_transport.longitude = transport.longitude
            existing_transport.minute_price = transport.minutePrice
            existing_transport.day_price = transport.dayPrice

            await session.commit()
            return existing_transport


@transport_controller.delete("/{id}")
async def delete_transport(id: int, user: User = Depends(current_user)):
    async with async_session_maker() as session:
        async with session.begin():
            stmt = select(Transport).where(Transport.id == id)
            result = await session.execute(stmt)
            existing_transport = result.scalars().first()

            if existing_transport == None:
                raise HTTPException(status_code=404, detail="Transport not found")

            if existing_transport.owner_id != user.id:
                raise HTTPException(status_code=403, detail="You are not the owner of this transport")

            query = (
                Transport.__table__.delete().where(Transport.id == id)
            )
            await session.execute(query)

            await session.commit()
            return existing_transport

