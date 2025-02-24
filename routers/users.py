from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from db.schemas import UpdateUserProfile, UserProfile
from models import User
from utils import get_current_user
import aiofiles
import json


router = APIRouter()


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: UserProfile = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """ This router returns response of the current user """
    return current_user  # FastAPI will automatically convert this to JSON


@router.put("/profile/edit", response_model=UpdateUserProfile)
async def edit_profile(profile_data: str = Form(...), image: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Update the current user's profile. """
    # Convert profile_data string to a dictionary
    try:
        profile_data = json.loads(profile_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON format for profile_data")
    
    if image:
        file_location = f"./media/dps/{image.filename}"
        
        # Save the uploaded image asynchronously
        async with aiofiles.open(file_location, "wb") as file_object:
            while chunk := await image.read(1024):
                await file_object.write(chunk)
    
    # update user profile fields
    current_user.profile_image = file_location

    # update user fields dynamically
    for field, value in profile_data.items():
        setattr(current_user, field, value if value is not None else getattr(current_user, field))

    await db.commit()
    await db.refresh(current_user)
    
    return current_user
