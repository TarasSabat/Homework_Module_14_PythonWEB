from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar
from src.database.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession):
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user with that email. If no such user exists, it returns None.

    :param email: str: Specify the email of the user we want to retrieve
    :param db: AsyncSession: Pass in the database connection
    :return: A user object
    :doc-author: Trelent
    """
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    return user


async def create_user(body: UserSchema, db: AsyncSession):
    """
    The create_user function creates a new user in the database.

    :param body: UserSchema: Validate the request body
    :param db: AsyncSession: Create a database session
    :return: A new user object
    :doc-author: Trelent
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Get the user object from the database
    :param token: str | None: Specify the type of the token parameter
    :param db: AsyncSession: Pass the database session to the function
    :return: The user object
    :doc-author: Trelent
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.


    :param email: str: Specify the email of the user to be confirmed
    :param db: AsyncSession: Pass in the database session
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
    The update_avatar_url function updates the avatar url of a user.

    :param email: str: Find the user in the database
    :param url: str | None: Specify that the url parameter can be either a string or none
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    return user

