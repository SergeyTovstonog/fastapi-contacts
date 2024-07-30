import os

from dotenv import load_dotenv

load_dotenv()

MAIL_USERNAME = os.getenv("MAIL_USERNAME", "test")
MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "test")
MAIL_FROM=os.getenv("MAIL_FROM", "admin@23web.com")
MAIL_PORT=os.getenv("MAIL_PORT", 1025)
MAIL_SERVER=os.getenv("MAIL_SERVER", "localhost")