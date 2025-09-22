# Future Migrations

This directory is for NEW database migrations created by agents.

## Naming Convention
- Use sequential numbers: 005_feature_name.sql, 006_another_feature.sql
- Keep names descriptive

## Before Creating a Migration
1. Check DATABASE_COMPLETE.md for current state
2. Review TABLES_DETAILED.md for existing columns
3. Ensure your changes don't conflict

## Migration Template
```sql
-- Migration XXX: Brief Description
-- Date: YYYY-MM-DD
-- Author: [Agent Name]

-- Your SQL changes here
```

## Important
- The documentation files in parent directory show CURRENT state
- Migrations here are for FUTURE changes only
- Always test migrations in development first