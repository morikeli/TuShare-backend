from .auth_schema import ConfirmResetPasswordSchema, LoginRequest, LoginResponse, RequestEmailVerificationSchema, ResetPasswordSchema
from .booking_schema import BookingResponse, CreateBooking
from .messages_schema import MessageCreate, MessageResponse
from .rides_schema import RideCreate, RideResponse
from .user_schema import CreateUser, CreatedUserResponse, UpdateUserProfile, UserProfile, UserModel


__all__ = [
    # auth schemas
    "ConfirmResetPasswordSchema",
    "LoginRequest",
    "LoginResponse",
    "RequestEmailVerificationSchema",
    "ResetPasswordSchema",

    # booking schemas
    "BookingResponse",
    "CreateBooking",

    # messages schemas
    "MessageCreate",
    "MessageResponse",

    # rides schemas
    "RideCreate",
    "RideResponse",

    # user schemas
    "CreateUser",
    "CreatedUserResponse",
    "UpdateUserProfile",
    "UserModel",
    "UserProfile",

]
