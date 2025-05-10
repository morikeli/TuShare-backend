from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, select
from sqlalchemy.orm import column_property, relationship

from ..core.database import Base
from .base import TimeStampMixin
from .user import User
import uuid


class Ride(Base, TimeStampMixin):
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


    def __repr__(self):
        return f"<Ride(id={self.id}, driver_id={self.driver_id}, vehicle_type={self.vehicle_type}, vehicle_plate={self.vehicle_plate})>"
