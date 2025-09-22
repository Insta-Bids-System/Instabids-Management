# Future Supabase Alignment Notes

- Verified that the existing `quotes` schema (from `004_marketplace_core.sql`) already provides the fields required by the web-form submission API, including `contractor_id`, `standardized_data`, and pricing/timeline columns.
- Updated the application service layer to resolve `contractor_id` via the `contractors` table, matching the foreign key definition in Supabase; no database changes are required.
- No new migrations are necessary at this time. Add additional SQL files in this folder if future Supabase updates are needed.
