from app import auth
from app.main import bp

from .views import ContractManagersView


def register_views():
    bp.add_url_rule(
        "/contract-managers",
        methods=["GET", "POST"],
        view_func=auth.login_required(ContractManagersView.as_view("contract_managers")),
    )


register_views()
