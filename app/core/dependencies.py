from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from typing import AsyncGenerator
from typing import Any, List

from .. import exceptions
from ..core.database import AsyncSessionLocal, get_db
from ..core.token_bearer import AccessTokenBearer
from ..models import User
from ..services import AuthService


auth_service = AuthService()


async def get_current_user(
    token: dict = Depends(AccessTokenBearer()),
    db: AsyncSession = Depends(get_db),
):
    user_email = token["user"]["email"]
    user = await auth_service.get_user_email(user_email, db)
    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles


    async def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        # Check if the user is verified
        if not current_user.is_verified:
            raise exceptions.AccountNotVerifiedException()

        if current_user.role in self.allowed_roles:
            return True

        raise exceptions.PermissionRequiredException()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db
        await db.close()
