from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from db.schemas import UpdateUserProfile
from models import User
from utils import get_current_user
import aiofiles
import os


router = APIRouter()


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(current_user: UserProfileResponse = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return current_user  # FastAPI will automatically convert this to JSON


@router.put("/profile/edit/")
async def edit_profile(profile_data: UpdateUserProfile, image: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    file_location = f"./media/dps/{image.filename}"
    
    # Save the uploaded image asynchronously
    async with aiofiles.open(file_location, "wb") as file_object:
        while chunk := await image.read(1024):
            await file_object.write(chunk)
    
    # update user profile fields
    current_user.profile_image = file_location

    # update user fields dynamically
    for field, value in profile_data.model_dump().items():
        setattr(current_user, field, value if value is not None else getattr(current_user, field))

    await db.commit()
    await db.refresh(current_user)
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "profile_image": f"/media/dps/{os.path.basename(file_location)}" if file_location else None,
         "facebook_handle": current_user.facebook_handle,
        "instagram_handle": current_user.instagram_handle,
        "twitter_handle": current_user.twitter_handle,
        "work_address": current_user.work_address,
        "home_address": current_user.home_address,
        "bio": current_user.bio
    }
