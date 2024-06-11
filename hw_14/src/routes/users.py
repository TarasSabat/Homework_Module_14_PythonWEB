import pickle

import cloudinary
import cloudinary.uploader
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config
from src.database.db import get_db
from src.services.auth import auth_service
from src.database.models import User
from src.schemas.user import UserResponse
from src.repository import users as repositories_users
from fastapi import Depends, UploadFile, File, APIRouter
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/users", tags=["users"])
cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


@router.get(
    "/me",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    """
    The get_current_user function is a dependency that will be injected into the
        get_current_user endpoint. It uses the auth_service to retrieve the current user,
        and returns it if found.

    :param user: User: Get the current user from the database
    :return: The current user
    :doc-author: Trelent
    """
    return user


@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(
    file: UploadFile = File(),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The get_current_user function is a dependency that will be used in the
        get_current_user endpoint. It takes an optional file and user parameter,
        which are both dependencies themselves. The file parameter is a File object,
        which represents an uploaded file from the client. The user parameter is a User object,
        which represents the current authenticated user.

    :param file: UploadFile: Get the file from the request body
    :param user: User: Get the user from the token
    :param db: AsyncSession: Get the database session
    :param : Get the current user
    :return: The user object
    :doc-author: Trelent
    """
    public_id = f"Web21/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repositories_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    return user
