from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from models import User
import aiofiles
import os

router = APIRouter()


@router.put("/profile/edit/")
async def edit_profile(image: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_db)):
    file_location = f"./media/dps/{image.filename}"
    
    # Save the uploaded image asynchronously
    async with aiofiles.open(file_location, "wb") as file_object:
        while chunk := await image.read(1024):
            await file_object.write(chunk)
    
    current_user.profile_image = file_location
    await db.commit()
    await db.refresh(current_user)
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "profile_image": f"/media/dps/{os.path.basename(file_location)}" if file_location else None
    }
