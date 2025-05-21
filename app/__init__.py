from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.database import init_db
from app.exceptions import (
    create_exception_handler,
    AccessTokenRequiredException,
    AccountNotVerifiedException,
    BookingAlreadyExistsException,
    BookingNotFoundException,
    CannotBookRideException,
    DestinationNotFoundException,
    DriverCannotBookRideException,
    InvalidTokenException,
    InvalidUserCredentialsException,
    NoSeatsLeftException,
    PasswordsDontMatchException,
    PasswordIsShortException,
    PermissionRequiredException,
    RefreshTokenRequiredException,
    RevokedTokenException,
    RideAlreadyExistsException,
    RideNotFoundException,
    UserAlreadyExistsException,
    UsernameAlreadyExistsException,
    UserNotFoundException,
)
from app.middleware import CustomAuthMiddleWare
from app.routers.auth import router as auth_router
from app.routers.messages import router as msg_router
from app.routers.rides import router as rides_router
from app.routers.users import router as users_router
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# API configration variables
api_version = 'v1'
docs_url = f"/api/{api_version}/docs"
redoc_url = f"/api/{api_version}/redoc"


# Define an asynchronous lifespan context manager for the FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    print('======='*10)     # for decoration
    logger.info('STARTING UP ... Initializing database.')
    await init_db()     # initialize database
    logger.info('DONE ... Database initialized.')
    print('======='*10)     # for decoration

    # Yield control back to the FastAPI application —
    # this allows the app to run while keeping the lifespan context open
    yield

    # this is displayed when the server is shutdown
    logger.warning('SHUTTING DOWN ... Cleaning up resources')
    logger.info('Wohoo! ... CLEAN UP COMPLETE')


app = FastAPI(
    lifespan=lifespan,
    docs_url=docs_url,
    redoc_url=redoc_url,
    title="TuShare API",
    description="API for TuShare, a ride-sharing application.",
    version="1.0.0",
)

# mount media files
app.mount("/media/dps", StaticFiles(directory="media/dps"), name="uploads")


# register middleware
app.add_middleware(CustomAuthMiddleWare)


# register endpoints
app.include_router(auth_router, prefix=f'/api/{api_version}/auth', tags=["Authentication"])
app.include_router(users_router, prefix=f'/api/{api_version}/users', tags=["Users"])
app.include_router(rides_router, prefix=f'/api/{api_version}', tags=["Rides"])
app.include_router(msg_router, prefix=f'/api/{api_version}', tags=["Messages"])


# register custom exceptions
app.add_exception_handler(AccessTokenRequiredException, create_exception_handler(403, "Authentication required!"))
app.add_exception_handler(AccountNotVerifiedException, create_exception_handler(403, "Please check your email and verify your account to use the app."))
app.add_exception_handler(BookingNotFoundException, create_exception_handler(404, "Booking not found!"))
app.add_exception_handler(InvalidTokenException, create_exception_handler(401, "Invalid to expired token provided!"))
app.add_exception_handler(InvalidUserCredentialsException, create_exception_handler(400, "Invalid user credentials."))
app.add_exception_handler(PasswordsDontMatchException, create_exception_handler(400, "Passwords don't match!"))
app.add_exception_handler(PasswordIsShortException, create_exception_handler(400, "Password is too short!"))
app.add_exception_handler(PermissionRequiredException, create_exception_handler(403, "You don't have permission to access this resource."))
app.add_exception_handler(RefreshTokenRequiredException, create_exception_handler(401, "Please provide a refresh token."))
app.add_exception_handler(RevokedTokenException,create_exception_handler(401, "This token was revoked! Please login again."))
app.add_exception_handler(UserAlreadyExistsException, create_exception_handler(409, "User with this email exists!"))
app.add_exception_handler(UsernameAlreadyExistsException, create_exception_handler(409, "The username is already taken!"))
app.add_exception_handler(UserNotFoundException, create_exception_handler(404, "User not found."))


# ride exception handlers
app.add_exception_handler(DestinationNotFoundException, create_exception_handler(404, "Destination not found!"))
app.add_exception_handler(RideNotFoundException, create_exception_handler(404, "Ride not found!"))
app.add_exception_handler(DriverCannotBookRideException, create_exception_handler(400, "Destination not found!"))
app.add_exception_handler(NoSeatsLeftException, create_exception_handler(400, "No seats left!"))
app.add_exception_handler(BookingAlreadyExistsException, create_exception_handler(400, "You have booked this ride!"))
app.add_exception_handler(CannotBookRideException, create_exception_handler(500, "Could not complete booking process! Please try again later."))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handles all unhandled exceptions globally in the FastAPI application.

    Logs the error details and returns a standardized JSON response with a
    status code of 500 (Internal Server Error). This helps avoid exposing
    sensitive details to the client while providing useful logs for debugging.

    Args:
        request (Request): The incoming HTTP request that caused the error.
        exc (Exception): The unhandled exception that occurred.

    Returns:
        JSONResponse: A response indicating an internal server error.
    """
    # Log the error with full traceback for debugging
    logger.fatal(f"Unhandled error: {exc}", exc_info=True)

    # Return a generic error message to the client to prevent exposing internal details
    return JSONResponse(
        status_code=500,
        content={"detail": "Oh snap! 😢 Internal server error."},
    )
