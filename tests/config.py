import tempfile

from app.config import Config


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SERVER_NAME = "localhost"
    RATELIMIT_ENABLED = False
    SECRET_KEY = "TEST_KEY"
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = tempfile.gettempdir()
