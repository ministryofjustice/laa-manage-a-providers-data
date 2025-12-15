from enum import Enum


class TagType(Enum):
    INACTIVE = ("Inactive", "govuk-tag--grey")
    ON_HOLD = ("On hold", "govuk-tag--yellow")
    FIRM_INTERVENED = ("Firm intervened", "govuk-tag--pink")
    FALSE_BALANCE = ("False balance", "govuk-tag--blue")
    DEBT_RECOVERY = ("Referred to debt recovery", "govuk-tag--pink referred-to-debt-recovery")

    def __init__(self, text, css_class):
        self.text = text
        self.css_class = css_class


class Tag:
    def __init__(self, tag_type):
        if not isinstance(tag_type, TagType):
            raise ValueError(f"tag_type must be a TagType enum value. Got: {type(tag_type)}")

        self.tag_type = tag_type

    def to_gov_params(self):
        return {"text": self.tag_type.text, "class": self.tag_type.css_class}

    def render(self) -> str:
        return f"<strong class='govuk-tag {self.tag_type.css_class}'>{self.tag_type.text}</strong>"
