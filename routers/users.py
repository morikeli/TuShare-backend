from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_db
from db.schemas import UpdateUserProfile, UserProfile
from config import UPLOAD_DIR
from models import User
from utils import get_current_user
import aiofiles
import json
import os


router = APIRouter()


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: UserProfile = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """ This router returns response of the current user """
    return current_user  # FastAPI will automatically convert this to JSON


@router.put("/profile/edit", response_model=UpdateUserProfile)
async def edit_profile(profile_data: str = Form(...), profile_pic: Optional[UploadFile] = File(None), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Update the current user's profile. """
    # Convert profile_data string to a dictionary
    try:
        profile_data = json.loads(profile_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON format for profile_data")
    
    if profile_pic:
        profile_image_path = os.path.join(UPLOAD_DIR, profile_pic.filename)
        
        # Save the uploaded image asynchronously
        async with aiofiles.open(profile_image_path, "wb") as file_object:
            while chunk := await profile_pic.read(1024):
                await file_object.write(chunk)
    
        # update user profile fields
        current_user.profile_image = profile_image_path
        print(f'User profile picture: {current_user.profile_image}')
    

    # Since mobile number is unique, check if mobile number exists before updating
    new_mobile_number = profile_data.get("mobile_number")
    if new_mobile_number and new_mobile_number != current_user.mobile_number:   # if "new_mobile_number" has a value and "new_mobile_number" is not the user's current mobile number
        stmt = select(User).where(User.mobile_number == new_mobile_number)
        result = await db.execute(stmt)
        existing_user = result.scalars().first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mobile number is already in use. Please provide a different number."
            )

    print(f'Profile data: {profile_data.items()}')
    # update user fields dynamically
    for field, value in profile_data.items():
        setattr(current_user, field, value if value is not None else getattr(current_user, field))

    try:
        await db.commit()
        await db.refresh(current_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update profile due to a constraint violation."
        )

    return current_user
