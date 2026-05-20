# SocialLens BI Warehouse

Run files in order against PostgreSQL:

```bash
psql "$DATABASE_URL" -f warehouse/schema/001_schema.sql
psql "$DATABASE_URL" -f warehouse/schema/002_indexes.sql
psql "$DATABASE_URL" -f warehouse/schema/003_views.sql
```

All warehouse objects live in schema `social_dw`.
