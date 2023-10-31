
from db import User, async_session_maker, Transport
from schemas import TransportCreateAdmin
from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from fastapi import HTTPException
from auth import fastapi_users


admin_transport_controller = APIRouter()
current_superuser = fastapi_users.current_user(active=True, superuser=True)


@admin_transport_controller.get("/")
async def get_all_transports(current_user: User = Depends(current_superuser)):
    async with async_session_maker() as session:
        async with session.begin():
            query = await session.execute(select(Transport))
            transports = query.scalars().all()

            if transports == None:
                raise HTTPException(status_code=404, detail="No transports found")

            return transports


@admin_transport_controller.get("/{id}")
async def get_transport(id: int, current_user: User = Depends(current_superuser)):
    async with async_session_maker() as session:
        async with session.begin():
            query = await session.execute(select(Transport).where(Transport.id == id))
            transport = query.scalars().first()

            if transport == None:
                raise HTTPException(status_code=404, detail="Transport not found")

            return transport


@admin_transport_controller.post("/")
async def create_transport(transport: TransportCreateAdmin, current_user: User = Depends(current_superuser)):
    async with async_session_maker() as session:
        async with session.begin():
            if transport.ownerId != None:
                query = await session.execute(select(User).where(User.id == transport.ownerId))

                if query.scalars().first() == None:
                    raise HTTPException(status_code=404, detail="User does not exist")

            new_transport = Transport(**transport.dict())
            session.add(new_transport)
            await session.commit()
            await session.refresh(new_transport)
            return new_transport


@admin_transport_controller.put("/{id}")
async def update_transport(id: int, transport: TransportCreateAdmin, current_user: User = Depends(current_superuser)):
    async with async_session_maker() as session:
        async with session.begin():
            query = await session.execute(select(Transport).where(Transport.id == id))
            transport_to_update = query.scalars().first()

            if transport_to_update == None:
                raise HTTPException(status_code=404, detail="Transport does not exist")

            if transport.ownerId != None:
                query = await session.execute(select(User).where(User.id == transport.ownerId))

                if query.scalars().first() == None:
                    raise HTTPException(status_code=404, detail="User does not exist")

            transport_to_update.owner_id = transport.ownerId
            transport_to_update.can_be_rented = transport.canBeRented
            transport_to_update.transport_type = transport.transportType
            transport_to_update.model = transport.model
            transport_to_update.color = transport.color
            transport_to_update.identifier = transport.identifier
            transport_to_update.description = transport.description
            transport_to_update.latitude = transport.latitude
            transport_to_update.longitude = transport.longitude
            transport_to_update.minute_price = transport.minutePrice
            transport_to_update.day_price = transport.dayPrice
            
            await session.commit()
            return transport_to_update


@admin_transport_controller.delete("/{id}")
async def delete_transport(id: int, current_user: User = Depends(current_superuser)):
    async with async_session_maker() as session:
        async with session.begin():
            query = await session.execute(select(Transport).where(Transport.id == id))
            transport_to_delete = query.scalars().first()

            if transport_to_delete == None:
                raise HTTPException(status_code=404, detail="Transport does not exist")

            query = (
                Transport.__table__.delete().where(Transport.id == id)
            )

            await session.execute(query)

            await session.commit()
            return transport_to_delete
