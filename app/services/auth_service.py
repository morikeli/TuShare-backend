from fastapi import HTTPException, UploadFile, status
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from .. import exceptions
from ..core.config import UPLOAD_DIR
from ..models import User
from ..schemas import CreateUser
from ..utils.auth import get_password_hash
import aiofiles
import os
import uuid


class AuthService:
    """
    Service class for handling user authentication and account management.
    """

    async def get_user_email(self, credentials: str, db: AsyncSession):
        """
        Asynchronously retrieves a user from the database by matching the provided credentials
        (either email or username).
        """

        stmt = select(User).where(or_(User.email==credentials, User.username==credentials))
        user = (await db.execute(stmt)).scalars().first()
        print(f"User: {user}")
        return user


    async def user_exists(self, email: str, db: AsyncSession) -> bool:
        """
        Check if a user with the given email exists in the database.
        """

        user = await self.get_user_email(email, db)
        return True if user else False


    async def create_user_account(self, user: CreateUser, profile_image: UploadFile | None, db: AsyncSession):
        """
        Asynchronously creates a new user account with optional profile image upload.
        """

        user_data = user.model_dump()

        user_email = user_data["email"]
        user_exists = await self.user_exists(user_email, db)

        if user_exists:
            raise exceptions.UserAlreadyExistsException()

        # Save the uploaded image to the server
        image_path = None
        # Handle optional image upload - check if the user has attached an image file in the frontend
        if profile_image:
            file_extension = os.path.splitext(profile_image.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            image_path = os.path.join(UPLOAD_DIR, unique_filename)

            # Save the uploaded image asynchronously
            async with aiofiles.open(image_path, "wb") as image_file:
                while chunk := await profile_image.read(1024):
                    await image_file.write(chunk)


        hashed_password = get_password_hash(user.password)

        # user_data = user.model_dump()
        user_data['profile_image'] = image_path
        user_data['password'] = hashed_password

        db_user = User(**user_data)

        try:
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)

            return db_user

        except IntegrityError as e:
            await db.rollback()  # Rollback the transaction to avoid issues

            # Check if the error is due to a unique constraint violation - user account already exists
            if "UNIQUE constraint failed" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username or email already exists. Please choose a different one."
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected database error occurred."
            )


    async def update_user_profile(self, user: User, user_data: dict, session: AsyncSession):
        """
        Asynchronously updates the profile information of a user with the provided data.
        """

        for key, value in user_data.items():
            setattr(user, key, value)

        await session.commit()
        return user
