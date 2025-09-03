from flask import flash, redirect, render_template, request, url_for

from app.services.contract_managers import ContractManagerService

from .forms import AddContractManagerForm, BulkRemoveContractManagerForm


def contract_managers_view():
    """Display and manage contract managers"""
    service = ContractManagerService()
    add_form = AddContractManagerForm()
    bulk_remove_form = BulkRemoveContractManagerForm()

    if request.method == "POST":
        if "add_manager" in request.form:
            if add_form.validate():
                if service.add(add_form.name.data):
                    flash(f"Added manager: {add_form.name.data}", "success")
                else:
                    flash("Manager already exists", "error")
                return redirect(url_for("main.contract_managers"))

        elif "remove_manager" in request.form:
            manager_name = request.form.get("name")
            if manager_name:
                if service.remove(manager_name):
                    flash(f"Removed manager: {manager_name}", "success")
                else:
                    flash("Manager not found", "error")
                return redirect(url_for("main.contract_managers"))

        elif "bulk_remove" in request.form:
            bulk_remove_form.selected_managers.data = request.form.getlist("selected_managers")

            if bulk_remove_form.validate():
                selected_managers = bulk_remove_form.selected_managers.data
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

    managers = service.get_all()

    return render_template(
        "contract_managers.html", add_form=add_form, bulk_remove_form=bulk_remove_form, managers=managers
    )
