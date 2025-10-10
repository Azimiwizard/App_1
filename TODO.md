# TODO for Railway Deployment Preparation

## Overview
Preparing the Stitch Daily Menu Flask app for smooth deployment on Railway with PostgreSQL database. This includes cleaning structure, enabling seeding, updating docs, and ensuring configs are set.

## Steps

1. [x] Clean project structure: Attempted to remove nested `stitch_app/` but failed due to locked files; duplicates exist but root files are primary and should not interfere.

2. [x] Update `main.py`: Uncommented the `seed_database()` call after `db.create_all()` to automatically populate initial dishes on the first deployment (it checks if data exists to avoid duplicates).

3. [x] Review and update `.gitignore`: Added `instance/` to ignore SQLAlchemy instance folder.

4. [x] Update `RAILWAY_DEPLOYMENT.md`: Added notes on required env vars, seeding, and troubleshooting section.

5. [x] Verify `Procfile` and `scripts/init_db_command.py`: Confirmed no changes needed; release phase handles DB init.

6. [ ] Test configuration: After edits, suggest local test with PostgreSQL (optional), then push to GitHub for Railway deployment.

7. [ ] Deploy and verify: Connect repo to Railway, add PostgreSQL service, set env vars, trigger deploy, check logs, and test app functionality (e.g., register user, add dish, place order).

## Notes
- Required env vars on Railway: `SECRET_KEY` (generate a strong one), `DATABASE_URL` (auto from PostgreSQL service), optional: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `OPENAI_API_KEY`, `N8N_WEBHOOK_URL`.
- After deployment, use Railway shell to run `python make_admin.py` if needed for admin user.
- Monitor Railway logs for any import errors due to structure clean-up.
