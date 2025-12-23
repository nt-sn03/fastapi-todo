from typing import Annotated
from uuid import uuid1
import shutil

from fastapi import Form, Depends, HTTPException, status, File, UploadFile
from fastapi.routing import APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..core.dependencies import get_db
from ..core.security import verify_token
from ..models.user import User
from ..models.task import Category
from ..schemas.categories import CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"])
security = HTTPBearer()


@router.post("/", response_model=CategoryResponse)
def create_categories(
    name: Annotated[str, Form()],
    color: Annotated[str, Form()],
    icon: Annotated[UploadFile, File()],
    db: Annotated[Session, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
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

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied."
        )

    existing_category = db.query(Category).filter(Category.name == name).first()
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists."
        )

    if icon.content_type not in ["image/svg+xml", "image/png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="icon should be svg format"
        )

    if icon.content_type == "image/svg+xml":
        icon_extention = "svg"
    elif icon.content_type == "image/png":
        icon_extention = "png"

    icon_path = f"media/category-icons/{str(uuid1())}.{icon_extention}"
    with open(icon_path, "wb") as f:
        shutil.copyfileobj(icon.file, f)

    new_category = Category(name=name, color=color, icon=icon_path)

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


@router.get("/")
def get_category_list():
    pass


@router.get("/{pk}")
def get_one_category(pk: int):
    pass


@router.put("/{pk}")
def update_category():
    pass


@router.delete("/{pk}")
def delete_category():
    pass
