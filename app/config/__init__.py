import logging
import os
from datetime import timedelta

from dotenv import load_dotenv

# Allows .env to be used in project for local development.
load_dotenv()


class Config(object):
    ENVIRONMENT = os.environ.get("MAPD_ENVIRONMENT", "production")
    LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", logging.INFO)
    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "")
    CONTACT_PHONE = os.environ.get("CONTACT_PHONE", "")
    DEPARTMENT_NAME = os.environ.get("DEPARTMENT_NAME", "MOJ Digital")
    DEPARTMENT_URL = os.environ.get("DEPARTMENT_URL", "https://mojdigital.blog.gov.uk/")
    SECRET_KEY = os.environ["SECRET_KEY"]
    SERVICE_NAME = "Manage a provider's data"
    SERVICE_PHASE = os.environ.get("SERVICE_PHASE", "Beta")
    SERVICE_URL = os.environ.get("SERVICE_URL", "")
    SESSION_COOKIE_HTTP_ONLY = ENVIRONMENT != "local"
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    SESSION_TIMEOUT = timedelta(minutes=30)
    SESSION_COOKIE_SECURE = True
    TESTING = True
    PDA_URL = os.environ.get("PDA_URL")
    PDA_ENVIRONMENT = os.environ.get("PDA_ENVIRONMENT")
    PDA_API_KEY = os.environ.get("PDA_API_KEY")
    PASSWORD = os.environ.get("PASSWORD")
