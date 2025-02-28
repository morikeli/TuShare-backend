from sqlalchemy import Column, Enum, Integer, String, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime, timezone
import uuid
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, "media")
DEFAULT_PROFILE_IMAGE_PATH = "/media/dps/default.png"


class User(Base):
    """ This is a user table  """
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4().hex), unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    username = Column(String, unique=True, index=True)
    bio = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    mobile_number = Column(String, unique=True, index=True)
    facebook_handle = Column(String, nullable=True)
    instagram_handle = Column(String, nullable=True)
    twitter_handle = Column(String, nullable=True)
    work_address = Column(String, nullable=True)
    home_address = Column(String, nullable=True)
    password = Column(String)
    profile_image = Column(String, nullable=True, default=DEFAULT_PROFILE_IMAGE_PATH)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    date_joined = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # New field to determine if user is a driver or passenger
    role = Column(Enum("passenger", "driver", name="user_role"), default="passenger", nullable=False)

    # Relationships
    rides = relationship("Ride", back_populates="driver")
    bookings = relationship("Booking", back_populates="passenger")


class Ride(Base):
    """ This is a rides table. It represents a ride offered by a driver. """
    __tablename__ = "rides"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4().hex), unique=True)
    driver_id = Column(String, ForeignKey("users.id"), nullable=False)
    vehicle_type = Column(String, nullable=False)  # e.g., Sedan, SUV, Bike
    vehicle_model = Column(String, nullable=True)
    vehicle_plate = Column(String, nullable=False, unique=True)
    available_seats = Column(Integer, nullable=False)
    departure_location = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    departure_time = Column(DateTime, nullable=False)
    price_per_seat = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    role = Column(Enum("passenger", "driver", name="user_role"), default="passenger", nullable=False)
    # Relationships
    driver = relationship("User", back_populates="rides")
    bookings = relationship("Booking", back_populates="ride")


class Booking(Base):
    """ Represents a booking made by a passenger. """
    __tablename__ = "bookings"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4().hex), unique=True)
    ride_id = Column(String, ForeignKey("rides.id"), nullable=False)
    passenger_id = Column(String, ForeignKey("users.id"), nullable=False)
    seats_booked = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(Enum("pending", "confirmed", "canceled", "completed", name="booking_status"), default="pending")

    # Relationships
    ride = relationship("Ride", back_populates="bookings")
    passenger = relationship("User", back_populates="bookings")


class TokenBlacklist(Base):
    """ In FastAPI, a logout mechanism typically involves invalidating the user's access token. 
        Since JWT tokens are stateless, you cannot "destroy" them on the server side. 
    """
    
    __tablename__ = "token_blacklist"

    token = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False)
