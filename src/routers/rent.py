
from db import User, Transport, Rent, async_session_maker
from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from fastapi import HTTPException
from auth import fastapi_users
from schemas import RentCreate
from datetime import datetime
from random import random


current_user = fastapi_users.current_user(active=True)
rent_controller = APIRouter()


@rent_controller.get("/Transport")
async def get_all_transports():
    async with async_session_maker() as session:
        async with session.begin():
            query = await session.execute(select(Transport).where(Transport.can_be_rented == True))
            rents = query.scalars().all()
            
            if rents == None:
                raise HTTPException(status_code=404, detail="No transports found")
                
            data = {}

            for rent in rents:
                data[rent.id] = {
                    "lat": rent.latitude,
                    "long": rent.longitude,
                    "radius": random() * 100,
                    "type": rent.transport_type
                }

            return data


@rent_controller.get("/MyHistory")
async def get_my_history(user: User = Depends(current_user)):
    rents_return = {}
    async with async_session_maker() as session:
       async with session.begin():
           query = await session.execute(select(Rent).where(Rent.user_id == user.id))
           rents = query.scalars().all()
           
           if rents == []:
               raise HTTPException(status_code=404, detail="No rents found")
           
           for rent in rents:
               rents_return[rent.id] = {
                    "transport_id": rent.transport_id,
                    "user_id": rent.user_id,
                    "rent_type": rent.rent_type,
                    "start_rent": rent.start_rent,
                    "end_rent": rent.end_rent,
                    "rent_price": rent.rent_price,
                    "final_price": rent.final_price
                }

           return rents_return


@rent_controller.get("/{rentId}")
async def get_rent(rent_id: int, user: User = Depends(current_user)):
    async with async_session_maker() as session:
        async with session.begin():
            query = await session.execute(select(Rent).where(Rent.id == rent_id))
            rent = query.scalars().first()
            
            if rent == None:
                raise HTTPException(status_code=404, detail="Rent not found")

            query = await session.execute(select(Transport).where(Transport.id == rent.transport_id))
            transport = query.scalars().first()

            if rent.user_id == user.id or transport.owner_id == user.id:
                return rent

            raise HTTPException(status_code=403, detail="You are not have access to this rent")



@rent_controller.get("/TransportHistory/{transportId}")
async def get_transport_history(transportId: int, user: User = Depends(current_user)):
    transport_id = transportId
    async with async_session_maker() as session:
        async with session.begin():
            query = await session.execute(select(Transport).where(Transport.id == transport_id))
            transport = query.scalars().first()
            
            if transport == None:
                raise HTTPException(status_code=404, detail="Transport not found")

            if transport.owner_id != user.id:
                raise HTTPException(status_code=403, detail="You are not have access to this transport")

            query = await session.execute(select(Rent).where(Rent.transport_id == transport_id))
            rents = query.scalars().all()

            return rents


@rent_controller.post("/New/{transportId}")
async def new_rent(transportId: int, rent: RentCreate, user: User = Depends(current_user)):
    transport_id = transportId
    async with async_session_maker() as session:
        async with session.begin():
            query = await session.execute(select(Transport).where(Transport.id == transport_id))
            transport = query.scalars().first()
            
            if transport == None:
                raise HTTPException(status_code=404, detail="Transport not found")

            if transport.owner_id == user.id:
                raise HTTPException(status_code=403, detail="You can not rent your own transport")

            if transport.can_be_rented == False:
                raise HTTPException(status_code=403, detail="This transport can not be rented")

            if rent.rent_type == "minute":
                if transport.minute_price == None:
                    raise HTTPException(status_code=400, detail="This transport can not be rented for minutes")
                price = transport.minute_price
            elif rent.rent_type == "day":
                if transport.day_price == None:
                    raise HTTPException(status_code=400, detail="This transport can not be rented for days")
                price = transport.day_price
            else:
                raise HTTPException(status_code=400, detail="Wrong rent type")

            new_rent = Rent(
                transport_id=transport_id,
                user_id=user.id,
                rent_type=rent.rent_type,
            )

            transport.can_be_rented = False
            
            session.add(new_rent)
            await session.commit()

            return new_rent


@rent_controller.put("/End/{rentId}")
async def end_rent(
    rentId: int,
    lat: float,
    long: float,
    user: User = Depends(current_user)
):
    async with async_session_maker() as session:
        async with session.begin():
            query = await session.execute(select(Rent).where(Rent.id == rentId))
            rent = query.scalars().first()

            if rent == None:
                raise HTTPException(status_code=404, detail="Rent not found")

            if rent.user_id != user.id:
                raise HTTPException(status_code=403, detail="You are not have access to this rent")

            query = await session.execute(select(Transport).where(Transport.id == rent.transport_id))
            transport = query.scalars().first()

            if transport == None:
                raise HTTPException(status_code=404, detail="Transport not found")

            if transport.can_be_rented == True:
                raise HTTPException(status_code=400, detail="This transport can not be rented")

            if rent.rent_type == "minute":
                rent.final_price = rent.rent_price * (datetime.utcnow() - rent.start_rent).seconds / 60
            elif rent.rent_type == "day":
                rent.final_price = rent.rent_price * (datetime.utcnow() - rent.start_rent).days
            else:
                raise HTTPException(status_code=400, detail="Wrong rent type")

            transport.latitude = lat
            transport.longitude = long

            rent.end_rent = datetime.strptime(datetime.utcnow().replace(microsecond=0).isoformat(), "%Y-%m-%dT%H:%M:%S")
            transport.can_be_rented = True

            await session.commit()

            return rent

