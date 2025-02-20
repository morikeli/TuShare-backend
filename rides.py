from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_db
from models import Ride, User

router = APIRouter()


@router.get("/rides/")
async def get_rides(db: AsyncSession = Depends(get_db)):
    stmt = select(Ride).where(Ride.booked_by == None)
    result = await db.execute(stmt)
    rides = result.scalars().all() 
    return rides


@router.post("/rides/{ride_id}/book/")
async def book_ride(ride_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_db)):
    stmt = select(Ride).where(Ride.booked_by == current_user.id)
    result = await db.execute(stmt)
    existing_booking = result.scalars().first()
    
    if existing_booking:
        raise HTTPException(status_code=400, detail="You already have a booked ride")
    
    q_stmt = select(Ride).where(Ride.id == ride_id)     # query statement
    result = await db.execute(q_stmt)
    ride = result.scalars().first()
    
    if ride is None or ride.booked_by is not None:
        raise HTTPException(status_code=404, detail="Ride not available")
    
    ride.booked_by = current_user.id
    await db.commit()
    await db.refresh(ride)
    return ride