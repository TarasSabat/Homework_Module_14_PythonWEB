from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy import or_, and_, func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


from src import schemas
from src.database.models import Contact, User
from src.schemas.contact import ContactBase


async def get_all_contacts(
    limit: int,
    offset: int,
    user: User,
    session: AsyncSession,
    # skip: int, limit: int, db: AsyncSession, user: User
) -> List[Contact]:
    """
    The get_contacts function returns a list of contacts for the user.

    :param skip: int: Skip the first n contacts
    :param limit: int: Limit the number of contacts returned
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Filter the contacts by user
    :return: A list of contact objects
    :doc-author: Trelent
    """
    query = (
        select(Contact).filter(Contact.user_id == user.id).offset(offset).limit(limit)
    )
    result = await session.execute(query)
    return result.scalars().all()


async def get_contact(
    contact_id: int,
    session: AsyncSession,
    user: User,
    # contact_id: int, db: AsyncSession, user: User
) -> Optional[Contact]:
    """
    The get_contact function returns a contact from the database.

    :param contact_id: int: Specify the contact id to be retrieved
    :param db: AsyncSession: Pass in the database session
    :param user: User: Get the user id from the user object
    :return: A contact object or none
    :doc-author: Trelent
    """
    query = select(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id)
    result = await session.execute(query)
    return result.scalars().first()


async def create_contact(
    contact: schemas.contact.ContactCreate, db: AsyncSession, user: User
):
    """
    The create_contact function creates a new contact in the database.
        Args:
            contact (schemas.contact.ContactCreate): The ContactCreate schema object that contains all of the information for creating a new contact in the database, including name, phone number and email address.
            db (AsyncSession): The SQLAlchemy AsyncSession object used to connect to and query our PostgreSQL database using SQLAlchemy's ORM syntax instead of raw SQL queries. This is passed into this function by dependency injection from FastAPI's Dependency Injection system which allows us to access it without having to import it directly into this file

    :param contact: schemas.contact.ContactCreate: Pass the contact data to the function
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user_id from the user object
    :return: A contact object
    :doc-author: Trelent
    """
    db_contact = Contact(**contact.dict(), user_id=user.id)
    db.add(db_contact)
    await db.commit()
    await db.refresh(db_contact)
    return db_contact


async def update_contact(
    contact_id: int, body: ContactBase, db: AsyncSession, user: User
) -> Optional[Contact]:
    """
    The update_contact function updates a contact in the database.

    :param contact_id: int: Identify the contact to be updated
    :param body: ContactBase: Pass the contact body to the function
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Ensure that the user is authorized to update the contact
    :return: The updated contact
    :doc-author: Trelent
    """
    query = select(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id)
    result = await db.execute(query)
    contact = result.scalars().first()
    if contact:
        for key, value in body.dict().items():
            setattr(contact, key, value)
        await db.commit()
        await db.refresh(contact)
    return contact


async def remove_contact(
    contact_id: int, db: AsyncSession, user: User
) -> Optional[Contact]:
    """
    The remove_contact function removes a contact from the database.

    :param contact_id: int: Specify the id of the contact to be deleted
    :param db: AsyncSession: Pass the database session into the function
    :param user: User: Get the user's id
    :return: The contact that was removed
    :doc-author: Trelent
    """
    query = select(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id)
    result = await db.execute(query)
    contact = result.scalars().first()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contacts(db: AsyncSession, query: str, user: User) -> List[Contact]:
    """
    The search_contacts function searches the database for contacts that match a given query.
    The function takes in two arguments:
        - db: The database session to use when querying the database.
        - query: The string to search for in the first_name, last_name, and email fields of all contacts.
    The function returns a list of Contact objects that match the given query.

    :param db: AsyncSession: Pass the database session to the function
    :param query: str: Search for contacts by first name, last name or email
    :param user: User: Filter the contacts by user
    :return: A list of contact objects
    :doc-author: Trelent
    """
    query = select(Contact).filter(
        or_(
            Contact.first_name.contains(query),
            Contact.last_name.contains(query),
            Contact.email.contains(query),
        ),
        Contact.user_id == user.id,
    )
    result = await db.execute(query)
    return result.scalars().all()


async def get_upcoming_birthdays(db: AsyncSession, user: User) -> List[Contact]:
    """
    The get_upcoming_birthdays function returns a list of contacts whose birthdays are within the next 7 days.

    :param db: AsyncSession: Pass in the database session
    :param user: User: Filter the contacts by user
    :return: A list of contacts whose birthday is within the next week
    :doc-author: Trelent
    """
    today = date.today()
    upcoming = today + timedelta(days=7)

    today_str = today.strftime("%m-%d")
    upcoming_str = upcoming.strftime("%m-%d")

    query = select(Contact).filter(
        Contact.user_id == user.id,
        or_(
            and_(
                func.to_char(Contact.birthday, "MM-DD") >= today_str,
                func.to_char(Contact.birthday, "MM-DD") <= upcoming_str,
            )
        ),
    )

    result = await db.execute(query)
    contacts = result.scalars().all()
    return contacts
