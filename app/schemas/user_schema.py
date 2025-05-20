from datetime import datetime
from fastapi import Form
from pydantic import BaseModel, EmailStr, Field, field_validator, StringConstraints
from typing import Annotated, List, Optional
from uuid import UUID

from ..schemas import BookingResponse, RideResponse


validated_mobile_num = Annotated[str, StringConstraints(min_length=10, max_length=15, pattern=r'^\+?[1-9]\d{1,14}$')]


class BaseUser(BaseModel):
    first_name: str
    last_name: str
    gender: str
    username: str
    email: EmailStr
    mobile_number: validated_mobile_num
    password: str


class CreateUser(BaseUser):
    """ This is a schema to create a user profile when a user creates an account. """
    pass

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


class CreatedUserResponse(BaseUser):
    id: str
    password: str | None = Field(default=None, exclude=True)


    class Config:
        from_attributes = True


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
    # @field_validator(
    #     "first_name", "last_name", "username", "bio", "mobile_number",
    #     "facebook_handle", "instagram_handle", "twitter_handle",
    #     "work_address", "home_address", "profile_image",
    #     mode="before"
    # )
    # def convert_none_to_empty_string(cls, value: Optional[str]) -> str:
    #     return "" if value is None else value

    # Convert datetime to string (ISO format)
    @field_validator("date_joined", mode="before")
    def convert_datetime_to_string(cls, value: Optional[datetime]) -> str:
        return value.isoformat() if value is not None else ""

    class Config:
        from_attributes = True

class UserModel(UserProfile):
    rides: List[RideResponse]
    bookings: List[BookingResponse]


class UpdateUserProfile(BaseModel):
    """ This is a schema to update a user's profile. """
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

    @classmethod
    def as_form(
        cls,
        first_name: Optional[str] = Form(None),
        last_name: Optional[str] = Form(None),
        username: Optional[str] = Form(None),
        gender: Optional[str] = Form(None),
        bio: Optional[str] = Form(None),
        mobile_number: Optional[str] = Form(None),
        facebook_handle: Optional[str] = Form(None),
        instagram_handle: Optional[str] = Form(None),
        twitter_handle: Optional[str] = Form(None),
        work_address: Optional[str] = Form(None),
        home_address: Optional[str] = Form(None),
        profile_image: Optional[str] = Form(None)
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
            gender=gender,
            bio=bio,
            mobile_number=mobile_number,
            facebook_handle=facebook_handle,
            instagram_handle=instagram_handle,
            twitter_handle=twitter_handle,
            work_address=work_address,
            home_address=home_address,
            profile_image=profile_image,
        )


class UpdateUserProfileResponse(UpdateUserProfile):
    """ Response data when a user updates their profile. """
    id: UUID

