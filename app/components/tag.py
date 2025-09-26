from enum import Enum


class TagColor(Enum):
    GREY = "govuk-tag--grey"
    GREEN = "govuk-tag--green"
    TURQUOISE = "govuk-tag--turquoise"
    BLUE = "govuk-tag--blue"
    LIGHT_BLUE = "govuk-tag--light-blue"
    PURPLE = "govuk-tag--purple"
    PINK = "govuk-tag--pink"
    RED = "govuk-tag--red"
    ORANGE = "govuk-tag--orange"
    YELLOW = "govuk-tag--yellow"


class Tag:
    def __init__(self, text: str, color: TagColor):
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Text must be a non-empty string")

        if not isinstance(color, TagColor):
            raise ValueError(f"Color must be a TagColor enum value. Got: {type(color)}")

        self.text = text
        self.color = color

    @property
    def colour_class(self):
        return self.color.value

    def to_govuk_params(self):
        return {"text": self.text, "classes": self.colour_class}
