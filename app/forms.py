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
        self.capture_initial_data(**kwargs)

    def capture_initial_data(self, **kwargs):
        self._original_data = {}
        for name, field in self._fields.items():
            value = kwargs.get(name, field.default)
            if name == "csrf_token":
                continue
            if value == "":
                value = None

            self._original_data[name] = value

    def has_changed(self):
        form_data = {}
        for name, field in self._fields.items():
            value = field.data
            if name == "csrf_token":
                continue

            if value == "":
                value = None
            if isinstance(self._original_data.get(name), int) and isinstance(value, str):
                try:
                    value = int(value)
                except Exception:
                    pass

            form_data[name] = value

        return form_data != self._original_data

    def render_conditional(self, field, sub_field, conditional_value) -> str:
        """
        Make field conditional using govuk-frontend conditional logic
        :param field: The controlling field
        :param sub_field: The controlled field
        :param conditional_value: The value the controlling field should have to show the controlled field
        :return str: The render field and subfield:
        """

        sub_field_rendered = sub_field()
        conditional = {"value": conditional_value, "html": sub_field_rendered}
        params = {"params": {"items": [{"conditional": conditional}]}}
        return field(**params)


class NoChangesMixin:
    no_changes_error_message = "You have not changed anything. Cancel if you do not want to make a change."

    def validate(self, *args, **kwargs):
        valid = super().validate(*args, **kwargs)
        if valid and not self.has_changed():
            self.attach_no_change_error_to_element(self.no_changes_error_message)
            valid = False
        return valid

    def attach_no_change_error_to_element(self, error_message):
        self.form_errors.append(error_message)


class IgnoreReasonIfStatusUnchangedMixin:
    """
    A mixin that modifies has_changed() to allow reason-only updates
    when the 'status' is already 'Yes'.

    Change detection is bypassed if and only if both the 'status' and
    the pre-populated 'reason' are identical to the submitted data.
    """

    def has_changed(self):
        status_field = self.status
        reason_field = self.reason

        status_changed = status_field.data != status_field.object_data
        if status_changed:
            return True

        if status_field.data == "Yes":
            reason_changed = str(reason_field.data) != str(reason_field.object_data)

            if reason_changed:
                return True
            else:
                return False

        return super().has_changed()
