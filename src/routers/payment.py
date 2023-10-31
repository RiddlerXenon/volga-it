
from fastapi import APIRouter, Depends, HTTPException
from db import User, async_session_maker
from sqlalchemy.future import select
from auth import fastapi_users


payment_controller = APIRouter()
current_user = fastapi_users.current_user(active=True)


@payment_controller.get("/Hesoyam/{accountId}")
async def get_account(accountId: int, user: User = Depends(current_user)):
    async with async_session_maker() as session:
        async with session.begin():
            if user.is_superuser:
                query = await session.execute(select(User).where(User.id == accountId))
                existing_user = query.scalars().first()

                if existing_user == None:
                    raise HTTPException(status_code=404, detail="User not found")

                existing_user.balance += 250_000
                await session.commit()

                return {"message": "User balance updated"}

            elif user.id == accountId:
                query = await session.execute(select(User).where(User.id == accountId))
                existing_user = query.scalars().first()

                if existing_user == None:
                    raise HTTPException(status_code=404, detail="User not found")

                existing_user.balance += 250_000
                await session.commit()

                return {"message": "User balance updated"}

            else:
                raise HTTPException(status_code=403, detail="Access denied")
                    
