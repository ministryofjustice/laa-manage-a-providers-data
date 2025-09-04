from flask import abort, flash, redirect, render_template, request, session, url_for

from app.services.contract_managers import ContractManagerService
from app.views import BaseFormView

from .forms import AddContractManagerForm, BulkRemoveContractManagerForm


class ContractManagersView(BaseFormView):
    """Main view for displaying and managing contract managers"""

    template = "contract_managers.html"
    success_endpoint = "main.contract_managers"

    def get_context_data(self, add_form=None, bulk_remove_form=None, page=1, **kwargs):
        service = ContractManagerService()
        paginated_data = service.get_paginated(page=page, per_page=10)

        return {
            "add_form": add_form if add_form else AddContractManagerForm(),
            "bulk_remove_form": bulk_remove_form if bulk_remove_form else BulkRemoveContractManagerForm(page=page),
            "managers": paginated_data["managers"],
            "pagination_data": paginated_data,
            **(kwargs.get("context", {}) if "context" in kwargs else {}),
        }

    def get(self, **kwargs):
        if "MAPD.Admin" not in session.get("_logged_in_user", {}).get("roles", []):
            abort(403)
        page = int(request.args.get("page", 1))
        return render_template(self.get_template(), **self.get_context_data(page=page, **kwargs))

    def post(self, **kwargs):
        service = ContractManagerService()
        page = int(request.args.get("page", 1))

        if "add_manager" in request.form:
            form = AddContractManagerForm()
            if form.validate():
                service.add(form.name.data)
                flash(f"Added manager: {form.name.data}", "success")
                return redirect(url_for("main.contract_managers"))
            else:
                return render_template(self.get_template(), **self.get_context_data(add_form=form, page=page, **kwargs))

        elif "remove_manager" in request.form:
            manager_name = request.form.get("name")
            if manager_name:
                if service.remove(manager_name):
                    flash(f"Removed manager: {manager_name}", "success")
                else:
                    flash("Manager not found", "error")
            return redirect(url_for("main.contract_managers"))

        elif "bulk_remove" in request.form:
            form = BulkRemoveContractManagerForm(page=page)
            form.selected_managers.data = request.form.getlist("selected_managers")

            if form.validate():
                selected_managers = form.selected_managers.data
                removed_count = 0
                failed_removals = []

                for manager_name in selected_managers:
                    if service.remove(manager_name):
                        removed_count += 1
                    else:
                        failed_removals.append(manager_name)

                if removed_count > 0:
                    manager_word = "manager" if removed_count == 1 else "managers"
                    flash(f"Successfully removed {removed_count} {manager_word}", "success")

                if failed_removals:
                    flash(f"Failed to remove: {', '.join(failed_removals)}", "error")

                return redirect(url_for("main.contract_managers"))
            else:
                return render_template(
                    self.get_template(), **self.get_context_data(bulk_remove_form=form, page=page, **kwargs)
                )

        return redirect(url_for("main.contract_managers"))


class AddContractManagerView(BaseFormView):
    """Form view for adding contract managers"""

    form_class = AddContractManagerForm
    template = "contract_managers.html"
    success_endpoint = "main.contract_managers"

    def form_valid(self, form):
        service = ContractManagerService()
        service.add(form.name.data)
        flash(f"<b>Added contract manager: {form.name.data}</b>", "success")
        return super().form_valid(form)


class RemoveContractManagerView(BaseFormView):
    """View for removing individual contract managers"""

    template = "contract_managers.html"
    success_endpoint = "main.contract_managers"

    def post(self, **kwargs):
        manager_name = request.form.get("name")
        if manager_name:
            service = ContractManagerService()
            if service.remove(manager_name):
                flash(f"Removed manager: {manager_name}", "success")
            else:
                flash("Manager not found", "error")
        return redirect(url_for("main.contract_managers"))


class BulkRemoveContractManagerView(BaseFormView):
    """Form view for bulk removing contract managers"""

    form_class = BulkRemoveContractManagerForm
    template = "contract_managers.html"
    success_endpoint = "main.contract_managers"

    def form_valid(self, form):
        service = ContractManagerService()
        selected_managers = form.selected_managers.data
        removed_count = 0
        failed_removals = []

        for manager_name in selected_managers:
            if service.remove(manager_name):
                removed_count += 1
            else:
                failed_removals.append(manager_name)

        if removed_count > 0:
            manager_word = "manager" if removed_count == 1 else "managers"
            flash(f"Successfully removed {removed_count} {manager_word}", "success")

        if failed_removals:
            flash(f"Failed to remove: {', '.join(failed_removals)}", "error")

        return super().form_valid(form)
