from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Annotated, Optional
from datetime import datetime
from uuid import UUID


validated_mobile_num = Annotated[str, StringConstraints(min_length=10, max_length=15, pattern=r'^\+?[1-9]\d{1,14}$')]


class LoginResponse(BaseModel):
    """ This is a login response schema. It returns json data with the fields below. """
    access_token: str
    token_type: str
    username: str
    last_login: Optional[datetime]


class CreateUser(BaseModel):
    """ This is a schema to create a user profile when a user creates an account. """
    first_name: str
    last_name: str
    gender: str
    username: str
    email: EmailStr
    mobile_number: validated_mobile_num
    password: str


class UserProfile(BaseModel):
    """ This schema is the response model for the getting user profile in `/profile/` endpoint. """
    id: UUID
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    bio: str | None = None
    email: EmailStr
    mobile_number: str | None = None
    facebook_handle: str | None = None
    instagram_handle: str | None = None
    twitter_handle: str | None = None
    work_address: str | None = None
    home_address: str | None = None
    profile_image: str | None = None
    date_joined: datetime | None = None

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
