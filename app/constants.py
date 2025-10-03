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
# Some firms can be children of other firms.
# All firm types...
FIRM_TYPE_CHOICES = [
    ("Barrister", "Barrister"),
    ("Advocate", "Advocate"),
    ("Chambers", "Chambers"),
    ("Legal Services Provider", "Legal services provider"),
]
# ...but only these can be 'parent' firms
PARENT_FIRM_TYPE_CHOICES = [
    ("Chambers", "Chambers"),
    ("Legal Services Provider", "Legal services provider"),
]

CONSTITUTIONAL_STATUS_CHOICES = [
    ("Partnership", "Partnership"),
    ("Limited Company", "Limited Company"),
    ("Sole Practitioner", "Sole Practitioner"),
    ("LLP", "Limited Liability Partnership (LLP)"),
    ("Charity", "Charity"),
    ("Government Funded Organisation", "Government Funded Organisation"),
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

PAYMENT_METHOD_CHOICES = [
    ("Electronic", "Electronic"),
    ("Cheque", "Cheque"),
]

PROVIDER_ACTIVE_STATUS_CHOICES = [
    ("active", "Active"),
    ("inactive", "Inactive"),
]

OFFICE_ACTIVE_STATUS_CHOICES = [
    ("active", "Active"),
    ("inactive", "Inactive"),
]
