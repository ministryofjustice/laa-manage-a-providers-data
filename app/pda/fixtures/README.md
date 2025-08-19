# PDA Mock API Fixtures

This directory contains JSON fixture files used by the MockProviderDataApi for local development.

## Files

- **providers.json** - Provider firm data
- **offices.json** - Office data linked to providers via `_firmId`
- **contracts.json** - Contract data linked to offices via `_firmOfficeId` 
- **schedules.json** - Schedule data linked to offices via `_firmOfficeId`

## Usage

The MockProviderDataApi automatically loads these fixtures when initialized. Fields prefixed with underscore (`_firmId`, `_firmOfficeId`) are used for internal relationships and are filtered out of API responses.

## Data Relationships

```
Providers (1:many) → Offices (1:many) → Contracts
                                      → Schedules
```
