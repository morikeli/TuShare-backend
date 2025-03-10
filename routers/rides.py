from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import func
from db.database import get_db
from db.schemas import PassengerResponse, RideCreate, RideResponse
from models import Booking, Ride, User
from utils import get_current_user

router = APIRouter()


@router.get("/rides", response_model=list[RideResponse])
async def get_available_rides(destination: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),):
    """ Get all available rides that are not booked. """
    stmt = (
        select(Ride)
        .options(joinedload(Ride.driver))  # Auto-load driver details
        .where(
            func.lower(Ride.destination).ilike(f"%{destination.lower()}%"),     # case-insensitive destination
            Ride.available_seats > 0
        )
    )

    
    result = await db.execute(stmt)
    rides = result.scalars().all() 
    return rides


@router.get("/rides/booked", response_model=list[RideResponse])
async def get_user_booked_rides(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),):
    """ Get all rides booked by the current user along with the passengers. """
    
    # Fetch all rides booked by the current user
    stmt = select(Ride).join(Booking, Ride.id == Booking.ride_id).where(Booking.passenger_id == current_user.id)
    result = await db.execute(stmt)
    booked_rides = result.scalars().all()

    # Query all rides booked by the current user, where each ride includes all passengers who booked that ride
    stmt = (
        select(User.first_name, User.last_name, Ride.departure_location, User.profile_image, Booking.ride_id)
        .join(Booking, Booking.passenger_id == User.id)
        .join(Ride, Booking.ride_id == Ride.id)
        .where(Booking.ride_id.in_([ride.id for ride in booked_rides]))
    )

    passenger_results = await db.execute(stmt)

    # Organize passengers by ride_id
    passengers_by_ride = {}
    for row in passenger_results.all():
        passenger = PassengerResponse(
            name=f"{row.first_name} {row.last_name}",
            departure_location=row.departure_location,
            profile_image=row.profile_image
        )
        passengers_by_ride.setdefault(row.ride_id, []).append(passenger)

    # Use `.model_dump()` to automatically map Ride object fields
    # Convert ORM objects to dict before using Pydantic model
    ride_responses = [
        RideResponse(
            **{column.name: getattr(ride, column.name) for column in ride.__table__.columns},
            driver_name=ride.driver_name,
            driver_profile_image=ride.driver_profile_image,
            passengers=passengers_by_ride.get(ride.id, [])
        )
        for ride in booked_rides
    ]

    return ride_responses


@router.post("/{ride_id}/book", status_code=status.HTTP_201_CREATED, response_model=RideResponse)
async def book_ride(ride_id: str,  db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    """ Book an available ride. """
    # Fetch the ride with the driver info
    q_stmt = select(Ride, User).join(User, Ride.driver_id == User.id).where(Ride.id == ride_id)
    result = await db.execute(q_stmt)
    ride_data = result.first()

    
    if not ride_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ride not found")

    ride, driver = ride_data
    driver_name = driver.first_name + driver.last_name

    # Prevent drivers from booking their own rides
    if ride.driver_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Drivers cannot book their own rides.")

    if ride.available_seats <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No available seats left.")
    
    # Check if the user has already booked this ride
    booking_stmt = select(Booking).where(
        Booking.ride_id == ride_id, Booking.passenger_id == current_user.id
    )
    existing_booking = await db.execute(booking_stmt)

    if existing_booking.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You have already booked this ride"
        )

    # Create a new booking
    new_booking = Booking(
        ride_id=ride.id,
        passenger_id=current_user.id,
        seats_booked=1,  # Assuming 1 seat per booking
        total_price=ride.price_per_seat,  # Assuming price per seat
        status="pending"
    )

    db.add(new_booking)

    # Reduce available seats
    ride.available_seats -= 1

    try:
        await db.commit()
        await db.refresh(ride)

        # Convert SQLAlchemy model to dict and add driver_name dynamically
        ride_dict = ride.__dict__.copy()
        ride_dict["driver_name"] = driver_name

        return RideResponse.model_validate(ride_dict)

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
