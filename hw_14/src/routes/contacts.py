from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from src import schemas
from src.database.db import get_db
from src.database.models import User
from src.schemas.contact import ContactUpdate
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service


router = APIRouter(prefix="/contact", tags=["contacts"])


@router.post(
    "/",
    response_model=schemas.contact.Contact,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(seconds=30))],
)
async def create_contact(
    body: schemas.contact.ContactCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    The create_contact function creates a new contact in the database.
        The function takes a ContactCreate object as input, which is validated against the schema defined in schemas/contact.py
        The function also requires an authenticated user to be passed into it via dependency injection (see auth_service)

    :param body: schemas.contact.ContactCreate: Validate the request body
    :param db: AsyncSession: Pass the database connection to the repository function
    :param user: User: Get the current user
    :return: The new contact created
    :doc-author: Trelent
    """
    return await repository_contacts.create_contact(body, db, user)


@router.get(
    "s/all",
    response_model=List[schemas.contact.Contact],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    The read_contacts function returns a list of contacts.

    :param skip: int: Skip a certain number of contacts, for example if you want to get the second page
    :param limit: int: Limit the number of contacts returned
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_all_contacts(skip, limit, db, user)
    return contacts


@router.get(
    "/{contact_id}",
    response_model=schemas.contact.Contact,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    The read_contact function is used to retrieve a single contact from the database.
    It takes in an integer representing the ID of the contact, and returns a Contact object.

    :param contact_id: int: Specify the contact id to be retrieved
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user from the auth_service
    :return: A single contact
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.put("/{contact_id}", response_model=schemas.contact.Contact)
async def update_contact(
    contact_id: int,
    body: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    The update_contact function updates a contact in the database.
        It takes an id of the contact to update, and a body containing the new data for that contact.
        The function returns an updated Contact object.

    :param contact_id: int: Get the contact id from the url
    :param body: ContactUpdate: Get the data from the request body
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user from the auth_service
    :return: The updated contact
    :doc-author: Trelent
    """
    contact = await repository_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=schemas.contact.Contact)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    The remove_contact function removes a contact from the database.

    :param contact_id: int: Specify the contact id of the contact to be removed
    :param db: AsyncSession: Pass the database session to the repository
    :param user: User: Get the current user from the auth_service
    :return: The contact that was removed
    :doc-author: Trelent
    """
    contact = await repository_contacts.remove_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.get(
    "s/search/",
    response_model=List[schemas.contact.Contact],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def search_contacts(
    query: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    The search_contacts function searches for contacts in the database.
        It takes a query string and returns a list of contacts that match the query.

    :param query: str: Search for a contact
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user
    :return: A list of contacts that match the search query
    :doc-author: Trelent
    """
    contact = await repository_contacts.search_contacts(db, query, user)
    return contact


@router.get("s/upcoming_birthdays/", response_model=List[schemas.contact.Contact])
async def upcoming_birthdays(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    The upcoming_birthdays function returns a list of contacts with upcoming birthdays.

    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: A list of contacts with upcoming birthdays
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_upcoming_birthdays(db, user)
    return contact
