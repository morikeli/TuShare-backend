from datetime import datetime
from pydantic import BaseModel


class BookingBaseModel(BaseModel):

    ride_id: str
    seats_booked: str
    total_price: float


class CreateBooking(BookingBaseModel):
    pass

class BookingResponse(BookingBaseModel):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime
