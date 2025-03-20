from pydantic import BaseModel


class LoginResponse(BaseModel):
    """ This is a login response model. It returns json data with the fields below. """
    access_token: str
    token_type: str
