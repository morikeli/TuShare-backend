from datetime import datetime, timedelta, timezone
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.future import select
from passlib.context import CryptContext
from jose import jwt

from ..core.config import Config
from ..core.database import get_db
from ..models import User
import jwt
import logging
import uuid


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRY = Config.ACCESS_TOKEN_EXPIRY
SECRET_KEY = Config.SECRET_KEY

serializer = URLSafeTimedSerializer(secret_key=Config.SECRET_KEY, salt="email-configuration")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    """
    Hash a plain password using the configured password hashing context.

    Args:
        password (str): The plain password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    """
    Verifies that a plain text password matches a hashed password.

    Args:
        plain_password (str): The plain text password provided by the user.
        hashed_password (str): The hashed password stored in the database.

    Returns:
        bool: True if the plain password matches the hashed password, False otherwise.
    """

    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expiry: timedelta = None, refresh: bool = False) -> str:
    """
    Generates a JSON Web Token (JWT) access token with the provided user data and expiry.

    Args:
        data (dict): The user data to include in the token payload.
        expiry (timedelta, optional): The duration until the token expires.
            If not provided, a default expiry (ACCESS_TOKEN_EXPIRY) is used.
        refresh (bool, optional): Indicates if the token is a refresh token. Defaults to False.

    Returns:
        str: The encoded JWT access token as a string.

    Notes:
        - The payload includes the user data, expiration time, a unique JWT ID (jti), and a refresh flag.
        - The token is signed using the secret and algorithm specified in the Config class.
    """

    # Initialize the payload dictionary
    payload = {}

    # Add user data, expiration, unique token ID, and refresh flag to the payload
    payload["user"] = data
    payload["exp"] = datetime.now(timezone.utc) + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY))
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh

    # Encode the payload into a JWT using the configured secret and algorithm
    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM
    )

    return token    # Return the encoded JWT token as a string


def verify_access_token(token: str) -> dict:
    """
    Verifies and decodes a JWT access token.

    Args:
        token (str): The JWT access token to verify.

    Returns:
        dict: The decoded token data if verification is successful.
        None: If the token is invalid or verification fails.

    Raises:
        None: All exceptions are handled internally and logged.
    """

    try:
        token_data = jwt.decode(jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
        return token_data

    except jwt.PyJWTError as e:
        logging.exception(e)
        return None


def create_url_safe_token(data: dict):
    """
    Generates a URL-safe, serialized token from the provided data dictionary.

    Args:
        data (dict): The data to be serialized and encoded into the token.

    Returns:
        str: A URL-safe, serialized token representing the input data.
    """

    private_key = serializer.dumps(data)
    return private_key


def decode_url_safe_token(private_key: str, max_age=1800):
    """
    Decodes a URL-safe token using the provided private key.

    Args:
        private_key (str): The token to be decoded.
        max_age (int, optional): The maximum age (in seconds) the token is valid for. Defaults to 1800.

    Returns:
        Any: The decoded data if the token is valid.

    Raises:
        Exception: Logs and suppresses any exception that occurs during decoding.
    """

    try:
        data = serializer.loads(private_key, max_age=max_age)
        return data

    except Exception as e:
        logging.error(str(e))
