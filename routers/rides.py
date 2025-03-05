from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from db.database import get_db
from db.schemas import RideCreate, RideResponse
from models import Booking, Ride, User
from utils import get_current_user

router = APIRouter()


@router.get("/rides", response_model=list[RideResponse])
async def get_available_rides(destination: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),):
    """ Get all available rides that are not booked. """
    stmt = select(Ride).where(
        Ride.destination == destination,  # Match the requested destination
        Ride.available_seats > 0  # Ensure the ride still has seats left
    )
    
    result = await db.execute(stmt)
    rides = result.scalars().all() 
    return rides


@router.get("/rides/booked", response_model=list[RideResponse])
async def get_user_booked_rides(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),):
    """ Get all rides booked by the current user. """
    stmt = select(Ride).where(Ride.booked_by == current_user.id)
    result = await db.execute(stmt)
    booked_rides = result.scalars().all()

    return booked_rides


@router.post("/{ride_id}/book", status_code=status.HTTP_201_CREATED, response_model=RideResponse)
async def book_ride(ride_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),):
    """ Book an available ride. """
    # Fetch the ride
    q_stmt = select(Ride).where(Ride.id == ride_id)
    result = await db.execute(q_stmt)
    ride = result.scalars().first()
    
    if not ride:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ride not found")
    
    if ride.booked_by is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ride is already booked")
    
    # Assign ride to user
    ride.booked_by = current_user.id

    try:
        await db.commit()
        await db.refresh(ride)
        return ride
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Booking failed")


@router.post("/rides/new-ride", status_code=status.HTTP_201_CREATED, response_model=RideResponse)
async def post_ride(ride_data: RideCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),):
    """ Create a new ride (Only for drivers) """
    if current_user.role != "driver":
        raise HTTPException(status_code=403, detail="Only drivers can post rides")

    driver_name = f"{current_user.first_name} {current_user.last_name}"
    new_ride = Ride(**ride_data.model_dump(), driver_id=current_user.id)

    db.add(new_ride)
    await db.commit()
    await db.refresh(new_ride)

    return RideResponse(**new_ride.__dict__, driver_name=driver_name)
