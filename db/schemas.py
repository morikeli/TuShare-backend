from pydantic import BaseModel, StringConstraints
from typing import Annotated


validated_mobile_num = Annotated[str, StringConstraints(min_length=10, max_length=15, pattern=r'^\+?[1-9]\d{1,14}$')]


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    gender: str
    username: str
    email: str
    mobile_number: validated_mobile_num
    hashed_password: str
