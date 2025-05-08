from sqlalchemy import Column, DateTime, func


class TimeStampMixin:
    """
    Mixin to add automatic created_at and updated_at timestamp columns
    to SQLAlchemy models.

    - `created_at`: Automatically set to the current time when the record is created.
    - `updated_at`: Automatically set to the current time when the record is created,
        and automatically updated when the record is updated.
    """

    # Automatically set on insert using the database's current timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Automatically set on insert AND updated on any update
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

