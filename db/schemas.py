from fastapi import Form
from pydantic import BaseModel, EmailStr, Field, StringConstraints, field_validator
from typing import Annotated, List, Optional
from datetime import datetime
from uuid import UUID


validated_mobile_num = Annotated[str, StringConstraints(min_length=10, max_length=15, pattern=r'^\+?[1-9]\d{1,14}$')]


class LoginResponse(BaseModel):
    """ This is a login response schema. It returns json data with the fields below. """
    access_token: str
    token_type: str


class CreateUser(BaseModel):
    """ This is a schema to create a user profile when a user creates an account. """
    first_name: str
    last_name: str
    gender: str
    username: str
    email: EmailStr
    mobile_number: validated_mobile_num
    password: str

    @classmethod
    def as_form(
        cls,
        first_name: str = Form(...),    # expects 'first_name' from form data
        last_name: str = Form(...),    # expects 'last_name' from form data
        username: str = Form(...),    # expects 'username' from form data
        email: str = Form(...),    # expects 'email' from form data
        mobile_number: str = Form(...),    # expects 'mobile_number' from form data
        gender: str = Form(...),    # expects 'gender' from form data
        password: str = Form(...)    # expects 'password' from form data
    ):
        """
        Converts form data into a Pydantic model instance.
        This method is used with FastAPI's `Depends()` - in edit profile's router to allow
        handling form submissions while maintaining model validation.
        """
        return cls(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            mobile_number=mobile_number,
            gender=gender,
            password=password
        )


class UserProfile(BaseModel):
    """ This schema is the response model for the getting user profile in `/profile/` endpoint. """
    id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    email: EmailStr
    mobile_number: Optional[str] = None
    facebook_handle: Optional[str] = None
    instagram_handle: Optional[str] = None
    twitter_handle: Optional[str] = None
    work_address: Optional[str] = None
    home_address: Optional[str] = None
    profile_image: Optional[str] = None
    date_joined: Optional[datetime] = None

    # Convert None to an empty string
    @field_validator(
        "first_name", "last_name", "username", "bio", "mobile_number",
        "facebook_handle", "instagram_handle", "twitter_handle",
        "work_address", "home_address", "profile_image",
        mode="before"
    )
    def convert_none_to_empty_string(cls, value: Optional[str]) -> str:
        return "" if value is None else value

    # Convert datetime to string (ISO format)
    @field_validator("date_joined", mode="before")
    def convert_datetime_to_string(cls, value: Optional[datetime]) -> str:
        return value.isoformat() if value is not None else ""

    class Config:
        from_attributes = True


class UpdateUserProfile(BaseModel):
    """ This is a schema to update a user's profile. """
    id: UUID
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    gender: Optional[str]
    mobile_number: Optional[str]
    facebook_handle: Optional[str]
    instagram_handle: Optional[str]
    twitter_handle: Optional[str]
    work_address: Optional[str]
    home_address: Optional[str]
    bio: Optional[str]
    profile_image: Optional[str] = None


class RideCreate(BaseModel):
    """ This schema is used to create a new ride - when drivers want to share their rides. """
    vehicle_type: str = Field(..., example="Sedan")
    vehicle_model: Optional[str] = Field(None, example="Toyota Corolla")
    vehicle_plate: str = Field(..., example="ABC-1234")
    available_seats: int = Field(..., gt=0, example=3)
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
    receiver_id: Optional[str]  # Receiver's unique ID
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
