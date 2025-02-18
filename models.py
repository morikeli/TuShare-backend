from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import uuid

class User(Base):
    """ This is a user table  """
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4().hex), unique=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    mobile_number = Column(String, unique=True, index=True)
    facebook_handle = Column(String, nullable=True)
    instagram_handle = Column(String, nullable=True)
    twitter_handle = Column(String, nullable=True)
    work_address = Column(String, nullable=True)
    home_address = Column(String, nullable=True)
    hashed_password = Column(String)
    profile_image = Column(String, nullable=True)


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
