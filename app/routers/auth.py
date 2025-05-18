from datetime import datetime, timedelta
from fastapi import APIRouter, BackgroundTasks, Depends, File, status, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession


from .. import exceptions
from ..core.config import Config
from ..core.dependencies import RoleChecker, get_current_user, get_db
from ..core.redis import add_token_to_blacklist
from ..core.token_bearer import AccessTokenBearer, RefreshTokenBearer
from ..mails.send_mail import create_message, mail
from ..models import User
from ..schemas import (
    ConfirmResetPasswordSchema,
    CreateUser,
    CreatedUserResponse,
    LoginRequest,
    RequestEmailVerificationSchema,
    ResetPasswordSchema,
    UserModel,
)
from ..utils.auth import (
    create_access_token,
    create_url_safe_token,
    decode_url_safe_token,
    hash_password,
    verify_password,
)
from ..services.auth_service import AuthService


router = APIRouter()
service = AuthService()
REFRESH_TOKEN_EXPIRY = Config.REFRESH_TOKEN_EXPIRY
user_role = Depends(RoleChecker(["driver", "passenger"]))


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
    email_verification_link = f"http://{Config.DOMAIN}/api/v1/auth/verify-account/{private_key}"

    message = create_message(
        recipients=[new_user.email],
        subject="Verify your email",
        template_body={"user_name": new_user.username, "verification_link": email_verification_link}
    )
    bg_task.add_task(mail.send_message, message, template_name="email-verification.html")


    return JSONResponse(
        status_code=201,
        content={
            "message": "Account created successfully! Check your email to verify your account.",
            "user": CreatedUserResponse.model_validate(new_user).model_dump(),
        }
    )


@router.post("/request-verification-link")
async def request_email_verification_link(
    user_email: RequestEmailVerificationSchema,
    bg_task: BackgroundTasks,
    session: AsyncSession = Depends(get_db)
):
    """
    This endpoint allow users to request a verification link to be sent to their email address.

    Args:
        user_email (RequestEmailVerificationSchema): The schema containing the user's email address.
        bg_task (BackgroundTasks): FastAPI background task manager for sending emails asynchronously.
        session (AsyncSession, optional): Database session dependency.
    Raises:
        UserNotFoundException: If the user with the provided email does not exist.
    Returns:
        JSONResponse:
            - 200: If the verification email was sent successfully.
            - 400: If the user's email is already verified.
    """

    email = user_email.email

    # Check if user exists
    user = await service.get_user_email(email, session)

    if not user:
        raise exceptions.UserNotFoundException()

    if user.is_verified:
        return JSONResponse(
            status_code=400,
            content={"message": "Your email is already verified."},
        )

    # Create signed token
    token = create_url_safe_token({"email": email})
    verification_link = f"http://{Config.DOMAIN}/api/v1/auth/verify-account/{token}"

    # Send email
    message = create_message(
        recipients=[email],
        subject="Verify your email",
        template_body={
            "user_name": user.username,
            "verification_link": verification_link
        }
    )
    bg_task.add_task(mail.send_message, message, template_name="email-verification.html")

    return JSONResponse(
        status_code=200,
        content={"message": "Verification email sent. Please check your inbox."},
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


@router.get('/refresh-token')
async def refresh_token(token_data: dict = Depends(RefreshTokenBearer())):
    """
    Endpoint to refresh an access token using a valid refresh token.

    Args:
        token_data (dict): The decoded refresh token data, provided by the RefreshTokenBearer dependency.

    Returns:
        JSONResponse: A response containing a new access token and a success message if the refresh token is valid and not expired.

    Raises:
        InvalidTokenException: If the refresh token is invalid or expired.
    """

    expiry_timestamp = token_data["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(
            data={
                "email": token_data["user"]["email"],
                "user_id": token_data["user"]["user_id"],
            }
        )

        return JSONResponse(
            content={
                "message": "Access token refreshed successfully!",
                "access_token": new_access_token,
            }
        )

    raise exceptions.InvalidTokenException()


@router.get('/user/me', dependencies=[user_role], response_model=UserModel)
async def get_user_details(user = Depends(get_current_user)):
    """
    Retrieve the details of the currently authenticated user. This endpoint returns the user object
    representing the currently authenticated user.

    Depends on:
        get_current_user: Dependency that provides the current authenticated user.

    Returns:
        The user object representing the currently authenticated user.
    """

    return user


@router.post('/reset-password')
async def reset_password(user_email: ResetPasswordSchema, bg_task: BackgroundTasks, user: User = Depends(get_current_user)):
    """
    Handles password reset requests by generating a secure reset link and sending it to the user's email address.
    Args:
        user_email (ResetPasswordSchema): The schema containing the user's email address for password reset.
        bg_task (BackgroundTasks): FastAPI background task manager for sending the email asynchronously.
        user (User, optional): The currently authenticated user, injected via dependency.
    Returns:
        JSONResponse: A response indicating that the password reset instructions have been sent to the user's email.
    Raises:
        HTTPException: If the user is not authenticated or the email is invalid.
    Side Effects:
        Sends an email with a password reset link to the specified user.
    """

    email = user_email.email

    private_key = create_url_safe_token({"email": email})
    reset_password_link = f"http://{Config.DOMAIN}/api/v1/auth/confirm-reset-password/{private_key}"

    message = create_message(
        recipients=[email],
        subject="Reset your password",
        template_body={
            "user_name": user.username,
            "reset_password_link": reset_password_link
        }
    )
    bg_task.add_task(mail.send_message, message, template_name="reset_password.html")
    return JSONResponse(
        content={
            "message": "Please check your email for instructions to reset your password.",
        },
        status_code=200
    )


@router.post('/confirm-reset-password/{user_private_key}')
async def confirm_reset_password(
    user_private_key: str,
    password: ConfirmResetPasswordSchema,
    session: AsyncSession = Depends(get_db),
):
    """
    Resets the user's password after confirming the reset token and validating the new password.

    Args:
        user_private_key (str): The URL-safe token containing user identification (e.g., email).
        password (ConfirmResetPasswordSchema): Schema containing the new password and its confirmation.
        session (AsyncSession, optional): Database session dependency.

    Raises:
        PasswordIsShortException: If the new password is shorter than 8 characters.
        PasswordsDontMatchException: If the new password and confirmation do not match.
        UserNotFoundException: If no user is found with the provided email.

    Returns:
        JSONResponse: A response indicating whether the password reset was successful or if an error occurred.
    """

    new_password = password.new_password
    confirm_password = password.confirm_new_password

    if len(new_password) < 8:
        raise exceptions.PasswordIsShortException()

    if confirm_password != new_password:
        raise exceptions.PasswordsDontMatchException()

    user_data = decode_url_safe_token(user_private_key)
    user_email = user_data.get('email')

    if not user_email:
        return JSONResponse(
            content={
                "message": "Could not reset your password. An error ocurred!",
            },
            status_code=500,
        )

    # Check if user exists
    user = await service.get_user_email(user_email, session)

    if not user:
        raise exceptions.UserNotFoundException()

    user_hashed_password = hash_password(new_password)
    await service.update_user_profile(user, {'password': user_hashed_password}, session)
    return JSONResponse(
        content={
            "message": "Your password was reset successfully!"
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
