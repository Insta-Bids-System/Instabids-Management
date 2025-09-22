# Archived Migrations

## Why These Files Were Archived

The following SQL migration files have been archived because:
1. They have already been applied to the production database
2. Everything in them is fully documented in the parent directory's documentation files
3. Keeping them active was causing confusion for agents

## Archived Files
- `003_property_management.sql` - Property management tables and enums
- `004_marketplace_core.sql` - Marketplace, contractors, quotes tables

## Where to Find This Information Now

All the schema from these migrations is now documented in:
- `../DATABASE_COMPLETE.md` - Complete database overview
- `../TABLES_DETAILED.md` - Every column of every table
- `../API_EXAMPLES.md` - How to interact with these tables
- `../TRIGGERS_FUNCTIONS.md` - Database automation

## For Agents
- Use the documentation files to understand current database state
- Create NEW migrations in the `../future/` directory
- Start numbering from 005 onwards

Note: These archived files are kept for historical reference only. Do not apply them again.