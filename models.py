from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone
import uuid
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, "media")
DEFAULT_PROFILE_IMAGE_PATH = "/media/dps/default.png"


class User(Base):
    """ This is a user table  """
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4().hex), unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    mobile_number = Column(String, unique=True, index=True)
    facebook_handle = Column(String, nullable=True)
    instagram_handle = Column(String, nullable=True)
    twitter_handle = Column(String, nullable=True)
    work_address = Column(String, nullable=True)
    home_address = Column(String, nullable=True)
    hashed_password = Column(String)
    profile_image = Column(String, nullable=True, default=DEFAULT_PROFILE_IMAGE_PATH)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    date_joined = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Ride(Base):
    """ This is a rides table. Info about rides is stored here """
    __tablename__ = "rides"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4().hex), unique=True)
    driver_name = Column(String, index=True)
    origin = Column(String, index=True)
    destination = Column(String, index=True)
    price = Column(Float)
    booked_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    user = relationship("User")
