from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import column_property, relationship

from ..core.database import Base
from .base import TimeStampMixin
import uuid


class Booking(Base, TimeStampMixin):
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


    def __repr__(self):
        return f"<Booking(id={self.id}, ride_id={self.ride_id}, passenger_id={self.passenger_id})>"
