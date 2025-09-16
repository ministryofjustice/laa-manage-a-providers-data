# Add Barrister/Advocate Business Logic

## Overview
When adding a barrister or advocate to a chambers, they are created as separate provider entities linked to the parent chambers.

## Business Rules

### Data Creation Process
When a barrister/advocate is created, three entities are generated:

#### 1. Provider Firm
- **firm_name**: Barrister/advocate name from form
- **firm_type**: "Barrister" or "Advocate" 
- **solicitor_advocate**: "No" for barristers, "Yes" for advocates
- **advocate_level**: Selected from form
- **bar_council_roll**: Bar council roll number for barristers or Solicitors Regulation Authority roll number for advocates
- **parent_firm_id**: Links to parent chambers

#### 2. Head Office (Replicated from Chamber's head office)
- **Address details**: Copied from parent chambers' head office
- **Contact details**: Phone, email, DX details copied
- **Excluded fields**: IDs, office code, creation date (auto-generated)
- **Head office markers**: `head_office = "N/A"` and `is_head_office = True`

#### 3. Contacts (Replicated from Chamber's head office)
- All contacts from parent chambers' head office are copied
- Same names, emails, phone numbers, job titles, primary/secondary status
- Fresh `vendor_site_id` linking to the new head office

### Form Validation
- **Required fields**: Name, level, roll number
- **Length limits**: Names max 255 chars, roll numbers max 15 chars
- **Roll number types**: Bar Council for barristers, Solicitors Regulation Authority for advocates
