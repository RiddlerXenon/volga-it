
from db import User, Transport, Rent, async_session_maker
from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from schemas import RentCreateAdmin
from fastapi import HTTPException
from auth import fastapi_users
from sqlalchemy import delete
from datetime import datetime


current_superuser = fastapi_users.current_user(active=True, superuser=True)
admin_rent_controller = APIRouter()


@admin_rent_controller.get("/Rent/{rentId}")
async def get_rent(rentId: int, user: User = Depends(current_superuser)):
    async with async_session_maker() as session:
        stmt = select(Rent).filter(Rent.id == rentId)
        result = await session.execute(stmt)
        rent = result.scalars().first()

        if rent is None:
            raise HTTPException(status_code=404, detail="Rent not found")

        return rent


@admin_rent_controller.get("/UserHistory/{userId}")
async def get_user_history(userId: int, user: User = Depends(current_superuser)):
    async with async_session_maker() as session:
        stmt = select(User).filter(User.id == userId)
        result = await session.execute(stmt)
        user = result.scalars().first()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        stmt = select(Rent).filter(Rent.user_id == userId)
        result = await session.execute(stmt)
        rents = result.scalars().all()

        if rents == []:
            raise HTTPException(status_code=404, detail="Rents not found")

        return rents


@admin_rent_controller.get("/TransportHistory/{transportId}")
async def get_transport_history(transportId: int, user: User = Depends(current_superuser)):
    async with async_session_maker() as session:
        stmt = select(Transport).filter(Transport.id == transportId)
        result = await session.execute(stmt)
        transport = result.scalars().first()

        if transport is None:
            raise HTTPException(status_code=404, detail="Transport not found")

        stmt = select(Rent).filter(Rent.transport_id == transportId)
        result = await session.execute(stmt)
        rents = result.scalars().all()

        if rents is None:
            raise HTTPException(status_code=404, detail="Rents not found")

        return rents


@admin_rent_controller.post("/Rent")
async def create_rent(rent: RentCreateAdmin, user: User = Depends(current_superuser)):
    async with async_session_maker() as session:
        stmt = select(User).filter(User.id == rent.userId)
        result = await session.execute(stmt)
        user = result.scalars().first()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        stmt = select(Transport).filter(Transport.id == rent.transportId)
        result = await session.execute(stmt)
        transport = result.scalars().first()

        if transport is None:
            raise HTTPException(status_code=404, detail="Transport not found")

        if transport.owner_id == user.id:
            raise HTTPException(status_code=400, detail="User can't rent own transport")

        if transport.can_be_rented == False:
            raise HTTPException(status_code=400, detail="Transport can't be rented")

        if rent.priceType == "minute":
            if transport.minute_price is None:
                raise HTTPException(status_code=400, detail="Transport can't be rented by minute")

            if rent.timeEnd != None:
                try:
                    rent.timeEnd = datetime.strptime(rent.timeEnd, "%Y-%m-%dT%H:%M:%S")
                except:
                    raise HTTPException(status_code=400, detail="Invalid time format")
            try:
                rent.timeStart = datetime.strptime(rent.timeStart, "%Y-%m-%dT%H:%M:%S")
            except:
                raise HTTPException(status_code=400, detail="Invalid time format")

            new_rent = Rent(
                transport_id=rent.transportId,
                user_id=rent.userId,
                start_rent=rent.timeStart,
                end_rent=rent.timeEnd,
                rent_price=rent.priceOfUnit,
                rent_type=rent.priceType,
                final_price=rent.finalPrice
            )

            if rent.timeEnd is None:
                transport.can_be_rented = False
            
            session.add(new_rent)
            await session.commit()

            return rent

        elif rent.priceType == "day":
            if transport.day_price is None:
                raise HTTPException(status_code=400, detail="Transport can't be rented by day")

            if rent.timeEnd != None:
                try:
                    rent.timeEnd = datetime.strptime(rent.timeEnd, "%Y-%m-%dT%H:%M:%S")
                except:
                    raise HTTPException(status_code=400, detail="Invalid time format")
            try:
                rent.timeStart = datetime.strptime(rent.timeStart, "%Y-%m-%dT%H:%M:%S")
            except:
                raise HTTPException(status_code=400, detail="Invalid time format")

            new_rent = Rent(
                transport_id=rent.transportId,
                user_id=rent.userId,
                start_rent=rent.timeStart,
                end_rent=rent.timeEnd,
                rent_price=rent.priceOfUnit,
                rent_type=rent.priceType,
                final_price=rent.finalPrice
            )

            if rent.timeEnd is None:
                transport.can_be_rented = False

            session.add(new_rent)
            await session.commit()

            return rent

        else:
            raise HTTPException(status_code=400, detail="Invalid rent type")


@admin_rent_controller.post("/Rent/End/{rentId}")
async def end_rent(
    rentId: int, 
    lat: float,
    long: float, 
    user: User = Depends(current_superuser)
):
    async with async_session_maker() as session:
        async with session.begin():
            stmt = select(User).filter(User.id == user.id)
            result = await session.execute(stmt)
            user = result.scalars().first()

            if user is None:
                raise HTTPException(status_code=404, detail="User not found")

            stmt = select(Rent).filter(Rent.id == rentId)
            result = await session.execute(stmt)
            rent = result.scalars().first()

            if rent is None:
                raise HTTPException(status_code=404, detail="Rent not found")

            stmt = select(Transport).filter(Transport.id == rent.transport_id)
            result = await session.execute(stmt)
            transport = result.scalars().first()

            if transport is None:
                raise HTTPException(status_code=404, detail="Transport not found")

            if transport.can_be_rented == True:
                raise HTTPException(status_code=400, detail="Transport is not rented")
            
            rent.end_rent = datetime.strptime(datetime.utcnow().replace(microsecond=0).isoformat(), "%Y-%m-%dT%H:%M:%S")

            if rent.rent_type == "minute":
                rent.final_price = transport.minute_price * (rent.end_rent - rent.start_rent).seconds / 60                
            elif rent.rent_type == "day":
                rent.final_price = transport.day_price * (rent.end_rent - rent.start_rent).days
            else:
                raise HTTPException(status_code=400, detail="Invalid rent type")

            transport.can_be_rented = True
            transport.latitude = lat
            transport.longitude = long

            session.add(rent)
            await session.commit()

            return rent


@admin_rent_controller.put("/Rent/{id}")
async def update_rent(
    id: int,
    rent: RentCreateAdmin,
    user: User = Depends(current_superuser)
):
    async with async_session_maker() as session:
        async with session.begin():
            stmt = select(Rent).filter(Rent.id == id)
            result = await session.execute(stmt)
            rent_db = result.scalars().first()

            if rent_db is None:
                raise HTTPException(status_code=404, detail="Rent not found")

            stmt = select(User).filter(User.id == rent.userId)
            result = await session.execute(stmt)
            user = result.scalars().first()

            if user is None:
                raise HTTPException(status_code=404, detail="User not found")

            stmt = select(Transport).filter(Transport.id == rent.transportId)
            result = await session.execute(stmt)
            transport = result.scalars().first()

            if transport is None:
                raise HTTPException(status_code=404, detail="Transport not found")
            
            rent.timeStart = datetime.strptime(rent.timeStart, "%Y-%m-%dT%H:%M:%S")
            rent.timeEnd = datetime.strptime(rent.timeEnd, "%Y-%m-%dT%H:%M:%S")

            if rent.timeEnd < rent.timeStart:
                raise HTTPException(status_code=400, detail="Invalid time format")

            if rent.priceType != "minute" or rent.priceType != "day":
                raise HTTPException(status_code=400, detail="Invalid rent type")

            rent_db.user_id = rent.userId
            rent_db.transport_id = rent.transportId
            rent_db.start_rent = rent.timeStart
            rent_db.end_rent = rent.timeEnd
            rent_db.rent_price = rent.priceOfUnit
            rent_db.rent_type = rent.priceType
            rent_db.final_price = rent.finalPrice

            await session.commit()

            return rent


@admin_rent_controller.delete("/Rent/{rentid}")
async def delete_rent(rentid: int, user: User = Depends(current_superuser)):
    async with async_session_maker() as session:
        async with session.begin():
            stmt = select(Rent).filter(Rent.id == rentid)
            result = await session.execute(stmt)
            rent = result.scalars().first()

            if rent is None:
                raise HTTPException(status_code=404, detail="Rent not found")

            query = (
                delete(Rent)
                .where(Rent.id == rentid)
            )

            await session.execute(query)
            await session.commit()

            return {"message": "Rent deleted successfully"}

