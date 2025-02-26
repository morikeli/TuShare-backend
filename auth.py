from fastapi import APIRouter, Depends, HTTPException, File, status, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from config import UPLOAD_DIR
from db.database import get_db
from db.schemas import CreateUser, LoginResponse
from models import TokenBlacklist, User
from utils import get_current_user, verify_password, create_access_token
from utils import get_password_hash
from datetime import datetime, timezone
from pathlib import Path
import aiofiles
import os
import uuid


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()


@router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(or_(User.email == form_data.username, User.username == form_data.username))
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    # Update the last_login field
    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    access_token = create_access_token(data={"sub": user.username})     # generate access token
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        username=user.username,
        last_login=user.last_login
    )


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=CreateUser)
async def create_user(user: CreateUser = Depends(CreateUser.as_form), profile_image: UploadFile = File(None), db: AsyncSession = Depends(get_db)):
    
    # Save the uploaded image to the server
    image_path = None
    # Handle optional image upload - check if the user has attached an image file in the frontend
    if profile_image:
        file_extension = os.path.splitext(profile_image.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        image_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Save the uploaded image asynchronously
        async with aiofiles.open(image_path, "wb") as image_file:
            while chunk := await profile_image.read(1024):
                await image_file.write(chunk)

    
    hashed_password = get_password_hash(user.password)
    
    user_data = user.model_dump()
    user_data['profile_image'] = image_path
    user_data['password'] = hashed_password

    db_user = User(**user_data)

    try:
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return user
    
    except IntegrityError as e:
        await db.rollback()  # Rollback the transaction to avoid issues

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


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Logs out the current user by blacklisting their token.
    """
    token = current_user["token"]  # Extract token from request

    # Check if the token is already blacklisted
    existing_token = await db.execute(
        select(TokenBlacklist).where(TokenBlacklist.c.token == token)
    )
    
    if existing_token.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has expired!"
        )

    # Blacklist the token
    blacklist_entry = TokenBlacklist(token=token, created_at=datetime.now(timezone.utc))
    db.add(blacklist_entry)
    await db.commit()

    return {"message": "Successfully logged out"}
