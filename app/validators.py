from wtforms import ValidationError


class ValidateSearchResults:
    """Ccheck if search returned results, checks form.num_results to see how many results were returned."""

    def __init__(self, message=None):
        self.message = message or "No providers found. Check the spelling and search for something else."

    def __call__(self, form, field):
        if field.data and hasattr(form, "num_results") and form.num_results == 0:
            raise ValidationError(self.message)
