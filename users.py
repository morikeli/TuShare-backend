import os
import shutil
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Form
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import SessionLocal
from models import User
from utils import get_password_hash

router = APIRouter()

UPLOAD_DIR = "media/dps/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup/")
def create_user(
        first_name: str = Form(...), 
        last_name: str = Form(...),
        username: str = Form(...),
        email: str = Form(...),
        gender: str = Form(...),
        password: str = Form(...),
        profile_image: UploadFile = File(None),
        db: Session = Depends(get_db),

    ):
    
    # Save the uploaded image to the server
    image_path = None
    # Handle optional image upload - check if the user has attached an image file in the frontend
    if profile_image:
        file_extension = os.path.splitext(profile_image.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        image_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Save the uploaded image
        with open(image_path, "wb") as image_file:
            shutil.copyfileobj(profile_image.file, image_file)

    
    hashed_password = get_password_hash(password)
    db_user = User(first_name=first_name, last_name=last_name, username=username, email=email, gender=gender, profile_image=image_path, hashed_password=hashed_password)

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return {
            "id": db_user.id,
            "first_name": db_user.first_name,
            "last_name": db_user.last_name,
            "username": db_user.username,
            "email": db_user.email,
            "gender": db_user.gender,
            "profile_image": db_user.profile_image,
            "home_address": db_user.home_address,
            "work_address": db_user.work_address,
            "facebook_handle": db_user.facebook_handle,
            "instagram_handle": db_user.instagram_handle,
            "twitter_handle": db_user.twitter_handle
        }
    
    except IntegrityError as e:
        db.rollback()  # Rollback the transaction to avoid issues

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


@router.put("/profile/edit/")
def edit_profile(image: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_db)):
    file_location = f"./media/dps/{image.filename}"
    with open(file_location, "wb") as file_object:
        file_object.write(image.file.read())
    current_user.profile_image = file_location
    db.commit()
    db.refresh(current_user)
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "profile_image": f"/media/dps/{os.path.basename(file_location)}" if file_location else None
    }
