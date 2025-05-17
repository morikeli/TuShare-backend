from datetime import timedelta
from fastapi import APIRouter, BackgroundTasks, Depends, File, status, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession


from .. import exceptions
from ..core.config import Config
from ..core.dependencies import get_db
from ..core.redis import add_token_to_blacklist
from ..core.token_bearer import AccessTokenBearer
from ..mails.send_mail import create_message, mail
from ..schemas import CreateUser, CreatedUserResponse, LoginRequest
from ..utils.auth import create_access_token, create_url_safe_token, decode_url_safe_token, verify_password
from ..services.auth_service import AuthService


router = APIRouter()
service = AuthService()
REFRESH_TOKEN_EXPIRY = Config.REFRESH_TOKEN_EXPIRY


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(user_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticates a user and generates access and refresh tokens upon successful login.

    Args:
        user_data (LoginRequest): The login credentials provided by the user.
        db (AsyncSession, optional): The database session dependency.

    Raises:
        InvalidUserCredentialsException: If the user does not exist or the password is invalid.

    Returns:
        JSONResponse: A response containing a success message, access token, and refresh token.
    """

    data = user_data.model_dump()
    email = data["username"]
    password = data["password"]

    user = await service.get_user_email(email, db)

    if user is None:
        raise exceptions.InvalidUserCredentialsException()

    password_valid = verify_password(password, user.password)

    if not password_valid:
        raise exceptions.InvalidUserCredentialsException()

    access_token = create_access_token(
        data={
            "email": user.email,
            "user_id": user.id,
            "role": user.role,
        }
    )

    refresh_token = create_access_token(
        data={
            "email": user.email,
            "user_id": user.id,
        },
        expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
        refresh=True,
    )

    return JSONResponse(
        content={
            "message": "User logged in successfully!",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(
    bg_task: BackgroundTasks,
    user: CreateUser = Depends(CreateUser.as_form),
    profile_image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a new user account, uploads an optional profile image, and sends a verification email.

    Args:
        bg_task (BackgroundTasks): FastAPI background task manager for sending emails asynchronously.
        user (CreateUser): User registration data, parsed from form input.
        profile_image (UploadFile, optional): Optional profile image file uploaded by the user.
        db (AsyncSession): SQLAlchemy asynchronous database session dependency.

    Returns:
        JSONResponse: A response containing a success message and the created user's data if successful.
        status_code (int): HTTP status code indicating the result of the operation.
        201: Account created successfully.
        500: Internal server error if any error occurs during user creation or email sending.
        409: User with the provided email already exists.
        400: Invalid user credentials if the email is already taken or the password is invalid.
        403: User account not verified if the user tries to access a protected resource without verification.

    Raises:
        Exception: Rolls back the database transaction if any error occurs during user creation or email sending.
    """

    # Create an account for the user
    new_user = await service.create_user_account(user, profile_image, db)

    # email verification
    private_key = create_url_safe_token({"email": new_user.email})
    email_verification_link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{private_key}"

    message = create_message(
        recipients=[new_user.email],
        subject="Verify your email",
        template_body={"user_name": new_user.first_name, "verification_link": email_verification_link}
    )
    bg_task.add_task(mail.send_message, message, template_name="verification.html")


    return JSONResponse(
        status_code=201,
        content={
            "message": "Account created successfully! Check your email to verify your account.",
            "user": CreatedUserResponse.model_validate(new_user).model_dump(),
        }
    )


@router.get('/verify/{user_private_key}')
async def verify_email(user_private_key: str, db: AsyncSession = Depends(get_db)):
    """
    Verifies a user's email address using a provided private key.
    This endpoint decodes the provided user private key to extract the user's email,
    checks if the user exists in the database, and updates the user's profile to mark
    the account as verified. Returns a JSON response indicating the result of the verification.

    Args:
        user_private_key (str): The URL-safe token containing user information for verification.
        db (AsyncSession, optional): The database session dependency.

    Returns:
        JSONResponse: A response object with a message indicating success or failure of verification.

    Raises:
        UserNotFoundException: If the user with the provided email does not exist.
    """

    user_data = decode_url_safe_token(user_private_key)
    user_email = user_data.get('email')

    if not user_email:
        return JSONResponse(
            content={
                "message": "Could not verify your email. An error ocurred!",
            },
            status_code=500,
        )

    user = await service.get_user_email(user_email, db)
    if not user:
        raise exceptions.UserNotFoundException()

    await service.update_user_profile(user, {'is_verified': True}, db)
    return JSONResponse(
        content={
            "message": "User account verified successfully!"
        },
        status_code=200,
    )


@router.post('/logout', status_code=status.HTTP_200_OK)
async def logout(token_details: dict = Depends(AccessTokenBearer())):
    """
    Logs out the current user by blacklisting their access token.
    This endpoint extracts the JWT ID (jti) from the provided access token,
    adds it to a blacklist to prevent further use, and returns a success message.

    Args:
        token_details (dict): A dictionary containing details of the access token,
            injected via dependency (AccessTokenBearer).

    Returns:
        JSONResponse: A response indicating successful logout.

    Raises:
        HTTPException: If token extraction or blacklisting fails.
    """

    jti = token_details["jti"]
    await add_token_to_blacklist(jti)
    return JSONResponse(
        content={
            "message": "User logged out successfully!",
        }
    )
