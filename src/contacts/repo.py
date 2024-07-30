from sqlalchemy import select

from src.contacts.models import Contact
from src.contacts.schemas import ContactsCreate


class ContactsRepository:
    def __init__(self, session):
        self.session = session

    async def get_contacts(self, owner_id:int, limit: int = 10, offset: int = 0):
        query = select(Contact).where(Contact.owner_id == owner_id).offset(offset).limit(limit)
        results = await self.session.execute(query)
        return results.scalars().all()

    async def create_contacts(self, contact: ContactsCreate, owner_id: int):

        new_contact = Contact(**contact.model_dump(), owner_id=owner_id)
        self.session.add(new_contact)
        await self.session.commit()
        await self.session.refresh(new_contact)  # To get the ID from the database
        return new_contact

    async def search_contacts(self, query):
        q = select(Contact).filter(
            (Contact.first_name.ilike(query))
            | (Contact.last_name.ilike(query))
            | (Contact.email.ilike(query))
        )
        results = await self.session.execute(q)
        return results.scalars().all()

    async def delete_contact(self, contact_id: int, user_id: int):
        q = select(Contact).filter(Contact.id == contact_id).filter(Contact.owner_id == user_id)
        result = await self.session.execute(q)
        contact = result.scalar_one()
        await self.session.delete(contact)
        await self.session.commit()

    async def get_contacts_all(self, limit: int = 10, offset: int = 0):
        query = select(Contact).offset(offset).limit(limit)
        results = await self.session.execute(query)
        return results.scalars().all()
