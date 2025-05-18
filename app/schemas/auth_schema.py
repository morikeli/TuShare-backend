from pydantic import BaseModel, EmailStr


class LoginResponse(BaseModel):
    """ This is a login response model. It returns json data with the fields below. """
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    """ This is a login request model. It returns json data with the fields below. """
    username: str
    password: str


class RequestEmailVerificationSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    email: EmailStr


class ConfirmResetPasswordSchema(BaseModel):
    new_password: str
    confirm_new_password: str
