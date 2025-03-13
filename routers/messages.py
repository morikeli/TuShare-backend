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


@router.get("/{user_id}/messages", response_model=List[GroupChatResponse])
async def get_group_messages(user_id: str, db: AsyncSession = Depends(get_db)):
    """ 
    Fetch group chats for the logged-in user with latest message & unread count. 
    """

    # Get rides where the user is a driver
    driver_rides_query = select(Ride.id).where(Ride.driver_id == user_id)
    driver_rides = list((await db.execute(driver_rides_query)).scalars())

    # Get rides where the user is a passenger
    passenger_rides_query = select(Booking.ride_id).where(Booking.passenger_id == user_id)
    passenger_rides = list((await db.execute(passenger_rides_query)).scalars())

    # Combine all relevant rides
    all_ride_ids = set(driver_rides + passenger_rides)

    if not all_ride_ids:
        return []  # No group chats

    # Fetch latest message for each group chat
    latest_messages_query = (
        select(
            Message.ride_id,
            Message.content.label("latest_message"),
            Message.timestamp.label("latest_timestamp"),
        )
        .where(Message.ride_id.in_(all_ride_ids))
        .order_by(Message.ride_id, Message.timestamp.desc())
    )

    latest_messages = {}
    result = await db.execute(latest_messages_query)
    for row in result:
        if row.ride_id not in latest_messages:
            latest_messages[row.ride_id] = {
                "latest_message": row.latest_message,
                "latest_timestamp": row.latest_timestamp,
            }

    # Get unread message count per ride
    unread_count_query = (
        select(Message.ride_id, func.count(Message.id).label("unread_count"))
        .where(Message.ride_id.in_(all_ride_ids), Message.receiver_id == user_id, Message.is_read == False)
        .group_by(Message.ride_id)
    )

    unread_counts = {row.ride_id: row.unread_count for row in (await db.execute(unread_count_query)).all()}

    # Get ride details (driver info)
    rides_query = select(Ride).where(Ride.id.in_(all_ride_ids))
    rides = list((await db.execute(rides_query)).scalars())

    # Build the response using Pydantic schema
    group_chats = [
        GroupChatResponse(
            ride_id=ride.id,
            driver_name=ride.driver_name,
            driver_profile_image=ride.driver_profile_image,
            latest_message=latest_messages.get(ride.id, {}).get("latest_message", "No messages yet"),
            latest_timestamp=latest_messages.get(ride.id, {}).get("latest_timestamp"),
            unread_count=unread_counts.get(ride.id, 0),
        )
        for ride in rides
    ]

    return group_chats


@router.get("/{ride_id}/get")
async def get_group_chats(ride_id: str, db: AsyncSession = Depends(get_db)):
    """ 
    Get group messages for all passengers and the driver sharing the same ride.
    The messages are displayed in the group's chat screen.
    """

    # Get the ride details
    ride_query = select(Ride).where(Ride.id == ride_id)
    ride = (await db.execute(ride_query)).scalar_one_or_none()

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")

    # Get driver details
    driver_query = select(User).where(User.id == ride.driver_id)
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
            }
            for msg, sender in messages
        ],
        "group_members": group_members,     # Add group members separately
    }

    return response_data


@router.put("/mark-as-read/{user_id}/{ride_id}")
async def mark_messages_as_read(user_id: str, ride_id: str, db: AsyncSession = Depends(get_db)):
    """
        Marks all unread messages in a specific group chat (ride) as read for the given user.
    """
    # Fetch unread messages for this user in the specified ride
    result = await db.execute(
        select(Message)
        .where(
            Message.ride_id == ride_id,  # Ride chat
            Message.receiver_id == user_id,  # Messages meant for this user
            Message.is_read == False  # Only unread messages
        )
    )

    unread_messages = result.scalars().all()

    if not unread_messages:
        return {"message": "No unread messages."}

    # Update messages to mark them as read
    for msg in unread_messages:
        msg.is_read = True

    await db.commit()
    return {"message": f"{len(unread_messages)} messages marked as read."}
