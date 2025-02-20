import os
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models import User


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
