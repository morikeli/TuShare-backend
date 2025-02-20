from fastapi import APIRouter, Depends, HTTPException, File, Form, status, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import SessionLocal
from models import User
from utils import verify_password, create_access_token
from datetime import datetime, timezone
from utils import get_password_hash
import os
import shutil
import uuid


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()

# media folder for profile pictures
UPLOAD_DIR = "media/dps/"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/token/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Update the last_login field
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email,
            "gender": user.gender,
            "profile_picture": user.profile_image,
            "date_joined": user.date_joined
        }
    }
