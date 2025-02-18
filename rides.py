from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Ride, User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/rides/")
def get_rides(db: Session = Depends(get_db)):
    return db.query(Ride).filter(Ride.booked_by == None).all()

@router.post("/rides/{ride_id}/book/")
def book_ride(ride_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_db)):
    existing_booking = db.query(Ride).filter(Ride.booked_by == current_user.id).first()
    if existing_booking:
        raise HTTPException(status_code=400, detail="You already have a booked ride")
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if ride is None or ride.booked_by is not None:
        raise HTTPException(status_code=404, detail="Ride not available")
    ride.booked_by = current_user.id
    db.commit()
    db.refresh(ride)
    return ride