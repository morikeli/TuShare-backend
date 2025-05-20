from fastapi import Form, HTTPException, status, UploadFile
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from ..core.config import UPLOAD_DIR
from ..core.dependencies import get_current_user
from ..models import User
from ..schemas import UpdateUserProfile
import aiofiles
import json
import os


class UserService:
    """
    Service class for handling user-related operations.
    """


    async def update_user_profile(self, user_id: str, data: UpdateUserProfile, profile_pic: UploadFile, user: User, db: AsyncSession):
        """
        Asynchronously updates a user's profile information, including optional profile picture upload.

        Args:
            user_id (str): The unique identifier of the user to update.
            data (UpdateUserProfile): The data object containing updated user profile fields.
            profile_pic (UploadFile): The uploaded profile picture file (optional).
            user (User): The current user instance.
            db (AsyncSession): The asynchronous database session.

        Raises:
            HTTPException: If the new mobile number is already in use by another user.
            HTTPException: If a database constraint violation occurs during update.
            Exception: Re-raises any other exceptions encountered during the update process.

        Returns:
            User: The updated user instance.
        """
        # Check if the user ID matches the current user's ID
        if user_id != str(user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this user's profile."
            )
        
        user = await db.merge(user)     # Merge the current user with the database session
        user_data = data.model_dump()
        user_data["id"] = user_id    # Add user ID in the request data


        if profile_pic:
            profile_image_path = os.path.join(UPLOAD_DIR, profile_pic.filename)

            # Save the uploaded image asynchronously
            async with aiofiles.open(profile_image_path, "wb") as file_object:
                while chunk := await profile_pic.read(1024):
                    await file_object.write(chunk)

            # update user profile fields
            user.profile_image = profile_image_path


        # Since mobile number is unique, check if mobile number exists before updating
        new_mobile_number = user_data.get("mobile_number")
        if new_mobile_number and new_mobile_number != user.mobile_number:   # if "new_mobile_number" has a value and "new_mobile_number" is not the user's current mobile number
            stmt = select(User).where(User.mobile_number == new_mobile_number)
            result = await db.execute(stmt)
            existing_user = result.scalars().first()

            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Mobile number is already in use. Please provide a different number."
                )

        # update user fields dynamically
        for field, value in user_data.items():
            if hasattr(user, field):
                setattr(user, field, value if value is not None else getattr(user, field))

        try:
            await db.commit()
            await db.refresh(user)

        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update profile due to a constraint violation."
            )

        except Exception:
            await db.rollback()
            raise   # re-raise the original exception

        return user

