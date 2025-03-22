from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class RideCreate(BaseModel):
    """ This schema is used to create a new ride - when drivers want to share their rides. """
    vehicle_type: str = Field(..., example="Sedan")
    vehicle_model: Optional[str] = Field(None, example="Toyota Corolla")
    vehicle_plate: str = Field(..., example="ABC-1234")
    available_seats: int = Field(..., ge=0, example=3)
    departure_location: str = Field(..., example="Downtown")   # pickup point
    destination: str = Field(..., example="Airport")
    departure_time: datetime = Field(..., example="2025-03-05T15:30:00")
    price_per_seat: float = Field(..., gt=0, example=15.50)

    class Config:
        from_attributes = True


class PassengerResponse(BaseModel):
    """ Schema for returning passenger details. """
    name: str
    departure_location: str
    profile_image: Optional[str] = None

    class Config:
        from_attributes = True


class RideResponse(RideCreate):
    """ This schema returns a response object when booking or creating rides. """
    id: str  # Ride ID
    driver_id: str  # Driver's user ID
    driver_name: str  # Driver's full name
    driver_profile_image: Optional[str] = None  # Add profile picture field
    passengers: List[PassengerResponse] = []  # List of passengers
