from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class MessageBase(BaseModel):
    """ 
    Base schema for messages. 
    Defines common attributes shared by different message schemas.
    """
    sender_id: UUID  # Unique identifier of the sender
    receiver_id: UUID  # Unique identifier of the receiver
    content: str  # Message text content


class MessageCreate(BaseModel):
    """ 
    Schema for creating a new message. 
    Used when sending a message between users.
    """
    sender_id: str  # Sender's unique ID
    receiver_id: Optional[str] = None  # Receiver's unique ID
    ride_id: Optional[str]  # If the message is part of a ride-based group chat
    content: str  # Message content


class UserResponse(BaseModel):
    """ 
    Schema representing a user's profile information.
    Used to provide sender or receiver details in message responses.
    """
    id: str  # Unique identifier of the user
    first_name: str  # User's first name
    last_name: str  # User's last name
    profile_image: Optional[str]  # URL of the user's profile image (if available)

    class Config:
        from_attributes = True  # Enables ORM conversion for database models


class MessageResponse(BaseModel):
    """ 
    Schema representing a message response. 
    Includes message details and additional metadata.
    """
    id: str  # Unique message identifier
    content: str  # Message text
    timestamp: datetime  # Timestamp when the message was sent
    ride_id: str  # Ride ID associated with the group chat
    driver_name: str  # Name of the driver in the group chat
    driver_profile_image: Optional[str]  # Profile image of the driver (if available)
    group_members: List[UserResponse]  # List of passengers in the group chat

    class Config:
        from_attributes = True  # Enables ORM conversion for database models


class GroupChatResponse(BaseModel):
    """ 
    Schema for group chat response. 
    Used to display ride-based group chat details.
    """
    ride_id: str  # Ride ID associated with the group chat
    driver_name: str  # Name of the driver in the group chat
    driver_profile_image: Optional[str]  # Profile image of the driver (if available)
    latest_message: str  # Content of the most recent message in the chat
    latest_timestamp: Optional[datetime]  # Timestamp of the latest message
    unread_count: int  # Number of unread messages for the current user
