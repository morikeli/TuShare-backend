from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import column_property, relationship

from ..core.database import Base
from .base import TimeStampMixin
import uuid


class Message(Base, TimeStampMixin):
    """
    Database model for storing chat messages between users.
    Each message is linked to a sender and a receiver (both are users).
    """

    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4().hex), unique=True, index=True)
    sender_id = Column(String, ForeignKey("users.id"), nullable=False)      # ID of the user sending the message
    receiver_id = Column(String, ForeignKey("users.id"), nullable=True)    # ID of the user receiving the message, reciever can be null in group chat
    ride_id = Column(String, ForeignKey("rides.id"), nullable=False)    # Link messages to a ride
    content = Column(String, nullable=False)    # message text
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))    # timestamp when the message was sent
    is_read = Column(Boolean, default=False)


    # relationships to the User model
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id], lazy='joined')


    def __repr__(self):
        return f"<Message(id={self.id} , sender_id={self.sender_id}, receiver_id={self.receiver_id})>"
