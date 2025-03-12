from db.database import get_db
from db.schemas import GroupChatResponse, MessageCreate, MessageResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from typing import List
from models import Booking, Message, Ride, User


router = APIRouter(prefix='/message', tags=['Messages'])


@router.post("/send", response_model=MessageResponse)
async def send_message(message: MessageCreate, db: AsyncSession = Depends(get_db)):
    """ This is a router to send messages to other users - driver or passengers. """

    new_message = Message(**message.model_dump())
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message


@router.get("/{driver_id}/get")
async def get_group_messages(driver_id: str, db: AsyncSession = Depends(get_db)):
    """ This router gets group messages for passengers and driver sharing the same ride. """

    # Get the latest ride posted by this driver (assuming only one ride is relevant)
    ride_query = select(Ride).where(Ride.driver_id == driver_id).order_by(Ride.created_at.desc())
    ride = (await db.execute(ride_query)).scalar_one_or_none()

    if not ride:
        raise HTTPException(status_code=404, detail="Driver has no active rides.")

    # Get driver details
    driver_query = select(User).where(User.id == driver_id)
    driver = (await db.execute(driver_query)).scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found.")

    driver_name = f"{driver.first_name} {driver.last_name}"
    driver_profile_image = driver.profile_image

    # Get all messages related to this ride
    messages_query = (
        select(Message, User)
        .join(User, User.id == Message.sender_id)
        .where(Message.ride_id == ride.id)
        .order_by(Message.timestamp)
    )
    result = await db.execute(messages_query)
    messages = result.all()  # Returns (Message, User) tuples

    # Fetch all passengers who booked this ride
    bookings_query = select(Booking).where(Booking.ride_id == ride.id)
    bookings = list((await db.execute(bookings_query)).scalars())
    passenger_ids = {booking.passenger_id for booking in bookings}  # Unique passenger IDs

    # Get passenger details
    users_query = select(User).where(User.id.in_(list(passenger_ids)))
    passengers = list((await db.execute(users_query)).scalars())
    
    # Format passengers into UserResponse
    group_members = [
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile_image": user.profile_image,
        }
        for user in passengers
    ]

    # Format response
    response_data = {
        "ride_id": ride.id,
        "driver_name": driver_name,
        "driver_profile_image": driver_profile_image,
        "messages": [
            {
                "id": msg.id,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "sender": {
                    "id": sender.id,
                    "first_name": sender.first_name,
                    "last_name": sender.last_name,
                    "profile_image": sender.profile_image,
                },
                "group_members": group_members,
            }
            for msg, sender in messages
        ],

    }

    return response_data
