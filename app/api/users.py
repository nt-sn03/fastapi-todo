from typing import Annotated, Dict

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..core.security import verify_token
from ..core.dependencies import get_db
from ..models.user import User
from ..models.task import Task, TaskStatus
from ..schemas.user import UserProfile

router = APIRouter(prefix="/users", tags=["users"])

security = HTTPBearer()


@router.get("/profile", response_model=UserProfile)
def profile(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
):
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

    if not user.is_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied."
        )

    result = {
        "tasks_count": user.tasks.count(),
        "tasks_todo": user.tasks.filter(Task.status == TaskStatus.TODO).count(),
        "tasks_doing": user.tasks.filter(Task.status == TaskStatus.DOING).count(),
        "tasks_done": user.tasks.filter(Task.status == TaskStatus.DONE).count(),
    }

    return {"user": user, "result": result}
