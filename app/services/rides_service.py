from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.expression import func

from .. import exceptions
from ..models import Booking, Ride, User
from ..schemas import PassengerResponse, RideCreate, RideResponse


class RideService:
    """
    Service class for managing ride-related operations.

    This class provides asynchronous methods to:
        - Retrieve available rides matching a destination.
        - Fetch all rides booked by the current user, including passenger details.
        - Book a ride for a user, handling seat availability and preventing duplicate bookings.
        - Allow a user to share (create) a new ride as a driver.
    """

    async def get_rides(self, destination: str, db: AsyncSession):
        """
        Retrieve a list of available rides matching the given destination.
        Args:
            destination (str): The destination to search for. Must not be None.
            db (AsyncSession): The asynchronous database session.
        Returns:
            List[Ride]: A list of Ride objects that match the destination and have available seats.
        Raises:
            DestinationNotFoundException: If the destination is not provided (None).
        """

        # raise HTTP 404 if destination isn't provided or is not found
        if destination is None:
            raise exceptions.DestinationNotFoundException()

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


    async def get_rides_booked_by_current_user(self, user: User, db: AsyncSession):
        """
        Retrieves all rides booked by the current user, including detailed passenger information for each ride.

        Args:
            user (User): The current user whose booked rides are to be fetched.
            db (AsyncSession): The asynchronous database session for executing queries.

        Returns:
            List[RideResponse]: A list of RideResponse objects, each representing a ride booked by the user.
                Each RideResponse includes ride details, driver information, and a list of passengers (as PassengerResponse)
                who have booked the same ride.

        Raises:
            SQLAlchemyError: If a database error occurs during query execution.

        Example:
            rides = await get_rides_booked_by_current_user(current_user, db)
        """

        # Fetch all rides booked by the current user
        stmt = select(Ride).join(Booking, Ride.id == Booking.ride_id).where(Booking.passenger_id == user.id)
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


    async def book_a_ride(self, ride_id: str, user: User, db: AsyncSession):
        """
        Books a ride for a user if seats are available and the user is not the driver.

        Args:
            ride_id (str): The unique identifier of the ride to be booked.
            user (User): The user attempting to book the ride.
            db (AsyncSession): The asynchronous database session.

        Returns:
            RideResponse: The response model containing ride details and driver name.

        Raises:
            RideNotFoundException: If the ride does not exist.
            DriverCannotBookRideException: If the driver tries to book their own ride.
            NoSeatsLeftException: If there are no available seats left in the ride.
            BookingAlreadyExistsException: If the user has already booked this ride.
            CannotBookRideException: If the booking cannot be completed due to a database integrity error.
            Exception: For any other unexpected errors during the booking process.
        """

        # Fetch the ride with the driver info
        q_stmt = select(Ride).options(joinedload(Ride.driver)).where(Ride.id == ride_id)
        result = await db.execute(q_stmt)
        ride = result.scalars().first()


        if not result:
            raise exceptions.RideNotFoundException()

        driver_name = ride.driver.first_name + ride.driver.last_name

        # Prevent drivers from booking their own rides
        if ride.driver_id == user.id:
            raise exceptions.DriverCannotBookRideException()

        if ride.available_seats == 0:
            raise exceptions.NoSeatsLeftException()

        # Check if the user has already booked this ride
        booking_stmt = select(Booking).where(
            Booking.ride_id == ride_id, Booking.passenger_id == user.id
        )
        existing_booking = await db.execute(booking_stmt)

        if existing_booking.scalars().first():
            raise exceptions.BookingAlreadyExistsException()

        # Create a new booking
        new_booking = Booking(
            ride_id=ride.id,
            passenger_id=user.id,
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
            raise exceptions.CannotBookRideException()

        except Exception:       # catch any other error
            await db.rollback()
            raise   # re-raise the exception


    async def share_current_users_ride(self, ride_data: RideCreate, user: User, db: AsyncSession):
        """
        Shares the current user's ride by creating a new ride entry in the database.
        Args:
            ride_data (RideCreate): The data required to create a new ride.
            user (User): The user who is sharing the ride.
            db (AsyncSession): The asynchronous database session.
        Returns:
            RideResponse: The response object containing the newly created ride details along with the driver's name.
        """

        driver_name = f"{user.first_name} {user.last_name}"
        new_ride = Ride(**ride_data.model_dump(), driver_id=user.id)

        db.add(new_ride)
        await db.commit()
        await db.refresh(new_ride)

        return RideResponse(**new_ride.__dict__, driver_name=driver_name)

