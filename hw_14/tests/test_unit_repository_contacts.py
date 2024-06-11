import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, AsyncMock, Mock

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas.contact import ContactBase, ContactCreate, ContactUpdate, Contact
from src.repository.contacts import (
    get_all_contacts,
    get_contact,
    create_contact,
    update_contact,
    remove_contact,
    search_conнtacts,
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
                email="test_email_1",
                phone_number="test_phone_number_1",
                birthday="test_birthday_1",
                user=self.user,
            ),
            Contact(
                id=2,
                first_name="test_first_name_2",
                last_name="test_last_name_2",
                email="test_email_2",
                phone_number="test_phone_number_2",
                birthday="test_birthday_2",
                user=self.user,
            ),
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_all_contacts(limit, offset, self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        limit = 10
        offset = 0
        contact = [
            Contact(
                id=1,
                first_name="test_first_name_1",
                last_name="test_last_name_1",
                email="test_email_1",
                phone_number="test_phone_number_1",
                birthday="test_birthday_1",
                user=self.user,
            ),
            Contact(
                id=2,
                first_name="test_first_name_2",
                last_name="test_last_name_2",
                email="test_email_2",
                phone_number="test_phone_number_2",
                birthday="test_birthday_2",
                user=self.user,
            ),
        ]
        mocked_contact = Mock()
        mocked_contact.scalars.return_value.all.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact(limit, offset, self.session, self.user)
        self.assertEqual(result, contact)

    async def test_create_contact(self):
        body = ContactBase(
            first_name="test_first_name",
            last_name="test_last_name",
            email="test_email",
            phone_number="test_phone_number",
            birthday="test_birthday",
        )
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.title, body.title)
        self.assertEqual(result.description, body.description)

    async def test_update_contact(self):
        body = ContactUpdate(
            first_name="test_first_name",
            last_name="test_last_name",
            email="test_email",
            phone_number="test_phone_number",
            birthday="test_birthday",
            completed=True,
        )
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(
            id=1,
            first_name="test_first_name",
            last_name="test_last_name",
            email="test_email",
            phone_number="test_phone_number",
            birthday="test_birthday",
            user=self.user,
        )
        self.session.execute.return_value = mocked_contact
        result = await update_contact(1, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.title, body.title)
        self.assertEqual(result.description, body.description)

    async def test_remove_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(
            id=1,
            first_name="test_first_name",
            last_name="test_last_name",
            email="test_email",
            phone_number="test_phone_number",
            birthday="test_birthday",
            user=self.user,
        )
        self.session.execute.return_value = mocked_contact
        result = await remove_contact(1, self.session, self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()

        self.assertIsInstance(result, Contact)

    async def test_search_contacts(self):
        contacts = Contact(
            id=1,
            first_name="test_first_name",
            last_name="test_last_name",
            email="test_email",
            phone_number="test_phone_number",
            birthday="test_birthday",
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
            email="test_email",
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
