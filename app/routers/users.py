from fastapi import APIRouter, Depends, UploadFile, File
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.dependencies import get_current_user, get_db
from ..models import User
from ..schemas.user_schema import UpdateUserProfile, UpdateUserProfileResponse, UserProfile
from ..services.user_service import UserService


router = APIRouter()
service = UserService()


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: UserProfile = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """ This router returns response of the current user """
    return current_user  # FastAPI will automatically convert this to JSON


@router.put("/profile/{user_id}/edit", response_model=UpdateUserProfileResponse)
async def edit_profile(
    user_id: str,
    profile_data: UpdateUserProfile = Depends(UpdateUserProfile.as_form),
    profile_pic: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """ Update the current user's profile. """

    return await service.update_user_profile(user_id, profile_data, profile_pic, current_user, db)
