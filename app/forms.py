from flask_wtf import FlaskForm


class BaseForm(FlaskForm):
    template: str = "form.html"
    title: str = "Form Title"  # Supports line breaks with "\n"
    url: str = "example-form"
    caption: str | None = None  # Optional caption text that will render above the form title
    description: str | None = None  # Optional description text that will render under the form title
    submit_button_text: str = "Continue"  # Should be "Submit" on final page before creating a new entity.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_data = {
            name: kwargs.get(name, field.default) for name, field in self._fields.items() if name != "csrf_token"
        }

    def has_changed(self):
        form_data = {name: field.data for name, field in self._fields.items() if name != "csrf_token"}
        return form_data != self._original_data


class NoChangesMixin:
    no_changes_error_message = "You have not changed anything. Cancel if you do not want to make a change."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_data = {
            name: kwargs.get(name, field.default) for name, field in self._fields.items() if name != "csrf_token"
        }

    def has_changed(self):
        form_data = {name: field.data for name, field in self._fields.items() if name != "csrf_token"}
        return form_data != self._original_data

    def validate(self, *args, **kwargs):
        valid = super().validate(*args, **kwargs)
        if valid and not self.has_changed():
            self.form_errors.append(self.no_changes_error_message)
            valid = False
        return valid
