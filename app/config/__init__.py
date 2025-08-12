import logging
import os
from datetime import timedelta

import redis
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
    SECRET_KEY = os.environ.get("SECRET_KEY", "Change me")
    SERVICE_NAME = "Manage a provider's data"
    SERVICE_PHASE = os.environ.get("SERVICE_PHASE", "Beta")
    SERVICE_URL = os.environ.get("SERVICE_URL", "")
    SESSION_COOKIE_HTTP_ONLY = ENVIRONMENT != "local"
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    SENTRY_TRACES_SAMPLE_RATE = float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.01"))
    SENTRY_PROFILES_SAMPLE_RATE = float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.2"))

    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.Redis.from_url(os.environ.get("REDIS_URL", "redis://redis:6379/0"))
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    SESSION_TIMEOUT = timedelta(minutes=30)
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "true").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_DOMAIN = None  # Don't set domain for localhost
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_NAME = "session"
    
    PREFERRED_URL_SCHEME = os.environ.get("PREFERRED_URL_SCHEME", "https")

    TESTING = os.environ.get("TESTING", "False").lower() == "true"
    SKIP_AUTH = os.environ.get("ENTRA_ID_SKIP_AUTH", "false").lower() == "true"

    PDA_USE_MOCK_API = os.environ.get("PDA_USE_MOCK_API", "False").lower() == "true"
    PDA_URL = os.environ.get("PDA_URL")
    PDA_ENVIRONMENT = os.environ.get("PDA_ENVIRONMENT")
    PDA_API_KEY = os.environ.get("PDA_API_KEY")
