from flask import Blueprint

bp = Blueprint("main", __name__, template_folder="templates")

# Import modules after blueprint creation to avoid circular imports
from app.main import middleware  # noqa: E402,F401
from app.main import routes  # noqa: E402,F401
from app.main.add_a_new_provider import register_views  # noqa: E402,F401
