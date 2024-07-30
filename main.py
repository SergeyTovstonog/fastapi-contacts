from fastapi import FastAPI

from src.contacts.routers import router as router_contacts
from src.auth.routers import router as router_auth

app = FastAPI()

app.include_router(router_contacts, prefix="/contacts", tags=["contacts"])
app.include_router(router_auth, prefix="/auth", tags=["auth"])
