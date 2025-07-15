import os
from dotenv import load_dotenv
from datetime import timedelta

# Allows .env to be used in project for local development.
load_dotenv()


class Config(object):
    ENVIRONMENT = os.environ.get("MAPD_ENVIRONMENT", "production")
    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "")
    CONTACT_PHONE = os.environ.get("CONTACT_PHONE", "")
    DEPARTMENT_NAME = os.environ.get("DEPARTMENT_NAME", "MOJ Digital")
    DEPARTMENT_URL = os.environ.get("DEPARTMENT_URL", "https://mojdigital.blog.gov.uk/")
    SECRET_KEY = os.environ["SECRET_KEY"]
    SERVICE_NAME = "Manage a Provider's Data"
    SERVICE_PHASE = os.environ.get("SERVICE_PHASE", "Beta")
    SERVICE_URL = os.environ.get("SERVICE_URL", "")
    SESSION_COOKIE_HTTP_ONLY = ENVIRONMENT != "local"
    SENTRY_DSN = os.environ.get("SENTRY_DSN")

    SESSION_TYPE = 'redis'
    SESSION_REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    SESSION_COOKIE_SECURE = False  # Must be False for HTTP localhost
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_DOMAIN = None  # Don't set domain for localhost
    SESSION_COOKIE_SAMESITE = 'Lax'

    SESSION_COOKIE_NAME = 'session'

    TESTING = False
