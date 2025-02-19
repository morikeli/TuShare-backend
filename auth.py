from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from utils import verify_password, create_access_token
from datetime import datetime, timezone


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()

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
            "username": user.username,
            "email": user.email,
            "profile_picture": user.profile_image,
            "work_address": user.work_address,
            "home_address": user.home_address,
            "facebook_handle": user.facebook_handle,
            "instagram_handle": user.instagram_handle,
            "twitter_handle": user.twitter_handle
        }
    }
