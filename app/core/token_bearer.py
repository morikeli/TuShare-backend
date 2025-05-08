from fastapi import Request
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

from app import exceptions
from .redis import token_in_blacklist
from ..utils.auth import verify_access_token


class TokenBearer(HTTPBearer):
    """
    Custom HTTPBearer authentication class for FastAPI that validates and verifies JWT access tokens.

    This class extends the HTTPBearer authentication scheme to:
    - Extract and validate JWT tokens from the Authorization header.
    - Check if the token is valid and not revoked (e.g., not in a blacklist).
    - Enforce implementation of additional token verification logic via the `verify_access_token` method.
    Subclasses must implement the `verify_access_token` method to provide custom token validation logic.

    Args:
        auto_error (bool): Whether to automatically raise an HTTPException if authentication fails.

    Methods:
        __call__(request: Request) -> HTTPAuthorizationCredentials | None:
            Asynchronously extracts and validates the JWT token from the request.
            Raises custom exceptions if the token is invalid or revoked.
        token_valid(token: str) -> bool:
            Checks if the provided token is valid.
        verify_access_token(token_data):
            Abstract method to be implemented by subclasses for additional token verification.
    """

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials
        token_data = verify_access_token(token)

        if not self.token_valid(token):
            raise exceptions.InvalidTokenException()

        if await token_in_blacklist(token_data["jti"]):
            raise exceptions.RevokedTokenException()

        self.verify_access_token(token_data)
        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = verify_access_token(token)

        if token_data is None:
            return False

        return True

    def verify_access_token(self, token_data):
        raise NotImplementedError("Subclasses must implement this method.")


class AccessTokenBearer(TokenBearer):
    """
    AccessTokenBearer is a subclass of TokenBearer responsible for handling access token validation.

    Methods:
        verify_access_token(token_data: dict):
            Verifies the provided token data. Raises an AccessTokenRequiredException if the token is a refresh token
            instead of an access token.
    """

    def verify_access_token(self, token_data: dict):
        if token_data and token_data["refresh"]:
            raise exceptions.AccessTokenRequiredException()


class RefreshTokenBearer(TokenBearer):
    """
    A custom token bearer class for handling refresh tokens.
    This class extends the `TokenBearer` class to provide additional verification
    for refresh tokens. It ensures that the provided token data corresponds to a
    refresh token and raises an exception if it does not.

    Methods
    -------
    verify_access_token(token_data: dict)
        Verifies that the provided token data is a refresh token.
        Raises `RefreshTokenRequiredException` if the token is not a refresh token.
    Raises
    ------
    exceptions.RefreshTokenRequiredException
        If the provided token data does not indicate a refresh token.
    """

    def verify_access_token(self, token_data: dict):
        if token_data and not token_data["refresh"]:
            raise exceptions.RefreshTokenRequiredException()
