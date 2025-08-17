from typing import Literal

# Type aliases for validation
FirmType = Literal["Advocate", "Barrister", "Chambers", "Legal Services Provider"]
ConstitutionalStatus = Literal[
    "Charity", "Government Funded Organisation", "LLP", "Limited Company", "Partnership", "Sole Practitioner", "N/A"
]
AdvocateLevel = Literal["Pupil", "Junior", "KC"]
YesNo = Literal["Yes", "No"]
YN = Literal["Y", "N"]
YNOrNA = Literal["Y", "N", "N/A"]

# Choice definitions for forms
FIRM_TYPE_CHOICES = [
    ("Barrister", "Barrister"),
    ("Advocate", "Advocate"),
    ("Chambers", "Chambers"),
    ("Legal Services Provider", "Legal Services Provider"),
]

CONSTITUTIONAL_STATUS_CHOICES = [
    ("Charity", "Charity"),
    ("Government Funded Organisation", "Government Funded Organisation"),
    ("LLP", "LLP"),
    ("Limited Company", "Limited Company"),
    ("Partnership", "Partnership"),
    ("Sole Practitioner", "Sole Practitioner"),
]

ADVOCATE_LEVEL_CHOICES = [
    ("Pupil", "Pupil"),
    ("Junior", "Junior"),
    ("KC", "King's Counsel (KC, previously QC)"),
]

YES_NO_CHOICES = [
    ("Yes", "Yes"),
    ("No", "No"),
]

YN_CHOICES = [
    ("Y", "Y"),
    ("N", "N"),
]

YN_OR_NA_CHOICES = [
    ("Y", "Y"),
    ("N", "N"),
    ("N/A", "N/A"),
]
