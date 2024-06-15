import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, AsyncMock, Mock

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact as DBContact, User
from src.schemas.contact import ContactBase, ContactUpdate, Contact
from src.repository.contacts import (
    get_all_contacts,
    get_contact,
    create_contact,
    update_contact,
    remove_contact,
    search_contacts,
    get_upcoming_birthdays,
)


class TestAsyncContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(id=1, username="test_user", password="qwerty", confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_all_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(
                id=1,
                first_name="test_first_name_1",
                last_name="test_last_name_1",
                email="test1@example.com",
                phone_number="test_phone_number_1",
                birthday=date(2000, 1, 1),
                user=self.user,
            ),
            Contact(
                id=2,
                first_name="test_first_name_2",
                last_name="test_last_name_2",
                email="test2@example.com",
                phone_number="test_phone_number_2",
                birthday=date(2000, 2, 2),
                user=self.user,
            ),
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_all_contacts(limit, offset, self.user, self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contact_id = 1
        contact = Contact(
            id=contact_id,
            first_name="test_first_name_1",
            last_name="test_last_name_1",
            email="test1@example.com",
            phone_number="test_phone_number_1",
            birthday=date(2000, 1, 1),
            user=self.user,
        )
        mocked_contact = MagicMock()
        mocked_contact.scalars.return_value.first.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact(contact_id, self.session, self.user)
        self.assertEqual(result, contact)

    async def test_create_contact(self):
        body = ContactBase(
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@example.com",
            phone_number="test_phone_number",
            birthday=date(2000, 1, 1),
        )
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, DBContact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)

    async def test_update_contact(self):
        body = ContactUpdate(
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@example.com",
            phone_number="test_phone_number",
            birthday=date(2000, 1, 1),
        )
        contact = Contact(
            id=1,
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@example.com",
            phone_number="test_phone_number",
            birthday=date(2000, 1, 1),
            user=self.user,
        )
        mocked_contact = MagicMock()
        mocked_contact.scalars.return_value.first.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await update_contact(1, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)

    async def test_remove_contact(self):
        contact = Contact(
            id=1,
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@example.com",
            phone_number="test_phone_number",
            birthday=date(2000, 1, 1),
            user=self.user,
        )
        mocked_contact = MagicMock()
        mocked_contact.scalars.return_value.first.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await remove_contact(1, self.session, self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()

        self.assertIsInstance(result, type(contact))

    async def test_search_contacts(self):
        contacts = Contact(
            id=1,
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@example.com",
            phone_number="test_phone_number",
            birthday=date(2000, 1, 1),
            user=self.user,
        )
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = [contacts]
        self.session.execute.return_value = mocked_contacts
        result = await search_contacts(self.session, "test_first_name", self.user)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], contacts)

    async def test_get_upcoming_birthdays(self):
        contacts = Contact(
            id=1,
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@example.com",
            phone_number="test_phone_number",
            birthday=(date.today() + timedelta(days=5)),
            user=self.user,
        )
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = [contacts]
        self.session.execute.return_value = mocked_contacts
        result = await get_upcoming_birthdays(self.session, self.user)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], contacts)


if __name__ == "__main__":
    unittest.main()
