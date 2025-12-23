from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..core.security import verify_token
from ..models.user import User
from ..core.dependencies import get_db

security = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    decoded_token = verify_token(credentials.credentials)
    if decoded_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
        )

    user: User = db.query(User).get(decoded_token["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
        )

    return user


def get_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied."
        )

    return user


def get_user(user: Annotated[User, Depends(get_current_user)]) -> User:
    if not user.is_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied."
        )

    return user
