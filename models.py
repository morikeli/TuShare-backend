from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, select
from sqlalchemy.orm import column_property, relationship
from db.database import Base
from datetime import datetime, timezone
import uuid
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, "media")
DEFAULT_PROFILE_IMAGE_PATH = "media/dps/default.png"


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
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

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
    departure_location = Column(String, nullable=False)     # pickup point
    destination = Column(String, nullable=False)
    departure_time = Column(DateTime, nullable=False)
    price_per_seat = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    role = Column(Enum("passenger", "driver", name="user_role"), default="passenger", nullable=False)
    # Relationships
    driver = relationship("User", back_populates="rides")
    bookings = relationship("Booking", back_populates="ride")

    # Auto-fetch driver's name when querying rides
    driver_name = column_property(
        select(User.first_name + " " + User.last_name)
        .where(User.id == driver_id)
        .scalar_subquery()
    )

    # Auto-fetch driver's profile picture when querying data
    driver_profile_image = column_property(
        select(User.profile_image)
        .where(User.id == driver_id)
        .scalar_subquery()
    )


class Booking(Base):
    """ Represents a booking made by a passenger. """
    __tablename__ = "bookings"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4().hex), unique=True)
    ride_id = Column(String, ForeignKey("rides.id"), nullable=False)
    passenger_id = Column(String, ForeignKey("users.id"), nullable=False)
    seats_booked = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(Enum("pending", "confirmed", "canceled", "completed", name="booking_status"), default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

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


class Message(Base):
    """
        Database model for storing chat messages between users.
        Each message is linked to a sender and a receiver (both are users).
    """

    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4().hex), unique=True, index=True)
    sender_id = Column(String, ForeignKey("users.id"), nullable=False)      # ID of the user sending the message
    receiver_id = Column(String, ForeignKey("users.id"), nullable=True)    # ID of the user receiving the message, reciever can be null in group chat
    ride_id = Column(String, ForeignKey("rides.id"), nullable=False)    # Link messages to a ride
    content = Column(String, nullable=False)    # message text
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))    # timestamp when the message was sent
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_read = Column(Boolean, default=False)  

    # relationships to the User model 
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id], lazy='joined')
