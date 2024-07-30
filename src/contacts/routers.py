from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_db
from src.auth.models import User
from src.auth.schemas import RoleEnum
from src.auth.utils import get_current_user, RoleChecker
from src.contacts.repo import ContactsRepository
from src.contacts.schemas import ContactsCreate, ContactsResponse

router = APIRouter()


@router.get("/ping")
async def ping():
    return {"message": "pong"}


@router.post("/", response_model=ContactsResponse, dependencies=[Depends(RoleChecker([RoleEnum.ADMIN]))])
async def create_contacts(contact: ContactsCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    repo = ContactsRepository(db)
    return await repo.create_contacts(contact, current_user.id)


@router.delete("/{contact_id}", dependencies=[Depends(RoleChecker([RoleEnum.ADMIN]))])
async def delete_contact(contact_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    repo = ContactsRepository(db)
    await repo.delete_contact(contact_id, current_user.id)
    return {"message": f"Contact {contact_id} deleted"}


@router.get("/all/", response_model=list[ContactsResponse], dependencies=[Depends(RoleChecker([RoleEnum.ADMIN]))], tags=['admin'])
async def get_contacts_all(
    limit: int = 10, offset: int = 0, db: AsyncSession = Depends(get_db)
):
    repo = ContactsRepository(db)
    return await repo.get_contacts_all(limit, offset)

@router.get("/", response_model=list[ContactsResponse], dependencies=[Depends(RoleChecker([RoleEnum.USER, RoleEnum.ADMIN]))])
async def get_contacts(
    limit: int = 10, offset: int = 0, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    repo = ContactsRepository(db)
    return await repo.get_contacts(current_user.id, limit, offset)

@router.get("/search/", response_model=list[ContactsResponse])
async def search_contacts(query: str, db: AsyncSession = Depends(get_db)):
    repo = ContactsRepository(db)
    return await repo.search_contacts(query)
