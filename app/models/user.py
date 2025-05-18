from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Enum, String
from sqlalchemy.orm import relationship

from ..core.database import Base
from .base import TimeStampMixin
import uuid
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, "media")
DEFAULT_PROFILE_IMAGE_PATH = "media/dps/default.png"


class User(Base, TimeStampMixin):
    """ This is a user table  """
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4().hex), unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    username = Column(String, unique=True, index=True)
    bio = Column(String, nullable=True, default=None)
    email = Column(String, unique=True, index=True)
    mobile_number = Column(String, unique=True, index=True)
    facebook_handle = Column(String, nullable=True, default=None)
    instagram_handle = Column(String, nullable=True, default=None)
    twitter_handle = Column(String, nullable=True, default=None)
    work_address = Column(String, nullable=True, default=None)
    home_address = Column(String, nullable=True, default=None)
    password = Column(String)
    profile_image = Column(String, nullable=True, default=DEFAULT_PROFILE_IMAGE_PATH)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True, default=None)
    date_joined = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_verified = Column(Boolean, default=False)
    role = Column(Enum("passenger", "driver", name="user_role"), default="passenger", nullable=False)

    # Relationships
    rides = relationship("Ride", back_populates="driver")
    bookings = relationship("Booking", back_populates="passenger")


    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
