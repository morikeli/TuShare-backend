from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Any, Callable


class APIException(Exception):
    """ Base class for all exceptions in the Tushare API. """
    pass


class InvalidTokenException(APIException):
    """ Exception is thrown when user provided an expired invalid token. """
    pass


class RevokedTokenException(APIException):
    """ Exception is raised when a user has provided a revoked token. """
    pass


class AccessTokenRequiredException(APIException):
    """ Exception is raised when a user has provided an refresh token instead of an access token. """
    pass


class RefreshTokenRequiredException(APIException):
    """ Exception is raised when a user has provided an access token instead of a refresh token. """
    pass


class InvalidUserCredentialsException(APIException):
    """ Exception is thrown when a user has provided invalid credentials. """
    pass


class UserAlreadyExistsException(APIException):
    """ Exception is thrown when a user has provided an email that exists. """
    pass


class UsernameAlreadyExistsException(APIException):
    """ Exception is thrown when a user has provided a username that exists. """
    pass


class PermissionRequiredException(APIException):
    """ Exception is thrown when a user does not have permission to peform the current action or access an endpoint/resource. """
    pass


class AccountNotVerifiedException(APIException):
    """ Exception is thrown when a user tries to perform an action without verifying their account. """
    pass


class BookingNotFoundException(APIException):
    """ Exception is thrown when a booking is not found. """
    pass


class BookingAlreadyExistsException(APIException):
    """ Exception is thrown when a user tries to book the same ride. """
    pass


class CannotBookRideException(APIException):
    """ Exception is thrown when the app cannot complete the booking process. """
    pass



class DestinationNotFoundException(APIException):
    """ Exception is thrown when a destination is not found. """
    pass


class RideNotFoundException(APIException):
    """ Exception is thrown when a ride is not found. """
    pass


class RideAlreadyExistsException(APIException):
    """ Exception is thrown when a ride already exists. """
    pass


class DriverCannotBookRideException(APIException):
    """ Exception is thrown when a driver tries to book their own ride. """
    pass

class NoSeatsLeftException(APIException):
    """ Exception is thrown when a ride has no available seats left. """
    pass


class UserNotFoundException(APIException):
    """ Exception is thrown when a user is not found. """
    pass


class PasswordIsShortException(APIException):
    """ Exception is raised when password and confirm password is short. """
    pass


class PasswordsDontMatchException(APIException):
    """ Exception is raised if the password and confirm password don't match. """
    pass


def create_exception_handler(status_code: int, detail: Any) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exception: APIException):
        return JSONResponse(
            content={"detail": detail},
            status_code=status_code
        )

    return exception_handler
