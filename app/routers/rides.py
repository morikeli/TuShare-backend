from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.dependencies import get_db, get_current_user, RoleChecker
from ..models import User
from ..schemas.rides_schema import RideCreate, RideResponse
from ..services.rides_service import RideService


router = APIRouter()
drivers_only = Depends(RoleChecker(allowed_roles=["driver"]))
passengers_only = Depends(RoleChecker(allowed_roles=["passenger"]))
service = RideService()


@router.get("/rides", dependencies=[passengers_only], response_model=list[RideResponse])
async def get_available_rides(
    destination: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """ Get all available rides that are not booked. """

    return await service.get_rides(destination, db)


@router.get("/rides/booked", dependencies=[passengers_only], response_model=list[RideResponse])
async def get_user_booked_rides(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """ Get all rides booked by the current user along with the passengers. """

    return await service.get_rides_booked_by_current_user(current_user, db)


@router.post("/{ride_id}/book", status_code=status.HTTP_201_CREATED, response_model=RideCreate)
async def book_ride(
    ride_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """ Book an available ride. """

    return await service.book_a_ride(ride_id, current_user, db)


@router.post("/rides/new-ride", dependencies=[drivers_only], status_code=status.HTTP_201_CREATED, response_model=RideResponse)
async def share_your_ride(
    ride_data: RideCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """ Router to allow users to share their a new ride. """

    return await service.share_current_users_ride(ride_data, current_user, db)
