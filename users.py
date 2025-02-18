import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
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
def create_user(username: str, email: str, password: str, profile_image: UploadFile = File(...), db: Session = Depends(get_db)):
    # Save the uploaded image to the server
    image_path = os.path.join(UPLOAD_DIR, profile_image.filename)
    with open(image_path, "wb") as image_file:
        shutil.copyfileobj(profile_image.file, image_file)
    
    hashed_password = get_password_hash(password)
    db_user = User(username=username, email=email, profile_image=image_path, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/profile/edit/")
def edit_profile(image: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_db)):
    file_location = f"./images/{image.filename}"
    with open(file_location, "wb") as file_object:
        file_object.write(image.file.read())
    current_user.profile_image = file_location
    db.commit()
    db.refresh(current_user)
    return {"info": f"Profile image uploaded at {file_location}"}
