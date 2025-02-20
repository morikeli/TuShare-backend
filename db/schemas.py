from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Annotated, Optional


validated_mobile_num = Annotated[str, StringConstraints(min_length=10, max_length=15, pattern=r'^\+?[1-9]\d{1,14}$')]


class CreateUser(BaseModel):
    """ This is a schema to create a user profile when a user creates an account. """
    first_name: str
    last_name: str
    gender: str
    username: str
    email: EmailStr
    mobile_number: validated_mobile_num
    password: str


class UpdateUserProfile(BaseModel):
    """ This is a schema to update a user's profile. """
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    gender: Optional[str]
    mobile_num: Optional[validated_mobile_num]
    facebook_handle: Optional[str]
    instagram_handle: Optional[str]
    twitter_handle: Optional[str]
    work_address: Optional[str]
    home_address: Optional[str]
    bio: Optional[str]
