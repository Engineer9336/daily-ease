# Daily Ease
**Local Help. Trusted People. Easier Everyday Living.**

A Streamlit + SQLAlchemy local-services marketplace starter for villages, small towns and neighbourhoods in India. It includes customer and worker accounts, searchable worker profiles, service requests, an FAQ helper, and English/Hindi/Hinglish interface strings.

## Important status and limitations
This is a runnable MVP, not a fully audited production marketplace. Demo profiles are sample records and cannot receive bookings. Payments, SMS/OTP, identity-document verification, reviews/complaints workflows, external object storage, email notifications, and a staffed support channel are not implemented. Admin management currently provides basic statistics and worker activation toggles; verification approval, categories CRUD, complaints, and a full activity-log UI remain future work. Translation coverage is validated for the current translation dictionary, but some system-generated technical errors and a few admin/detail labels are still English. Do not advertise workers as verified: profiles start as **Unverified**. No real deployment has been performed by this project build.

## Requirements
Python 3.11+ recommended. Python 3.13 should also work with compatible wheels.

## Install and run locally
```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env  # optional; set values for your environment
streamlit run app.py
```
The app initializes the database and seeds clearly labelled demo workers on first run. Default database is `daily_ease.db` in the project folder. Never commit the database if it contains personal data.

## Accounts
Register a customer or worker in the UI. Worker registration creates a profile, which can be edited under **My profile**. Only non-demo worker profiles accept customer service requests. Demo profiles use sample credentials internally and cannot be booked.

## Create the first admin
Stop the app, activate the same virtual environment, and run:
```bash
python create_admin.py
```
Enter the admin email, name and a private password of at least 12 characters. The command creates or promotes the account; it does not print the password. Start the app again and log in with that account. Never commit credentials.

## Database configuration
SQLite is suitable for local development and tests. For production, set `DATABASE_URL` to a persistent PostgreSQL connection string, for example:
```text
postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
```
Configure this in the hosting provider's secret/environment settings, not in source control. Schema tables are created automatically on startup; this project does not yet include Alembic migrations. Back up persistent data before schema changes. Avoid ephemeral host filesystems for production database or uploads.

## Images
The app accepts JPG/JPEG/PNG images up to 5 MB and attempts to decode and re-encode uploads. Set `DAILY_EASE_UPLOAD_DIR` to a persistent volume for a single-server deployment. For horizontally scaled/ephemeral hosting, replace this with object storage (e.g. S3-compatible storage) before relying on profile photos. Local upload storage is not production-durable by default.

## Tests
```bash
pytest -q
```
Tests use an isolated temporary SQLite database and cover password hashing/login, duplicate registration, search/category filtering, request transitions/permissions, translation-key coverage, and profile authorization. The current test suite does not replace a full browser UI smoke test or security audit.

## GitHub upload
```bash
git init
git add .
git commit -m "Build Daily Ease MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```
Check `git status` and `.gitignore` before pushing. Never commit `.env`, `secrets.toml`, user uploads, or a production database.

## Streamlit Community Cloud deployment
1. Push this folder to a GitHub repository.
2. In Streamlit Community Cloud, create an app from that repository and set the main file path to `app.py`.
3. Use Python 3.11 where the deployment settings permit.
4. Add `DATABASE_URL` and any other secrets in app settings. Use a persistent managed PostgreSQL database for production data.
5. For profile photos, configure durable object storage or a persistent volume. Community Cloud local files should not be treated as permanent storage.
6. Deploy, then test account creation, login, profile editing, search, service request status transitions, and language selection on desktop and mobile.

## Open on a phone
After deployment, open the actual deployed HTTPS URL in Chrome (Android) or Safari (iPhone). Android: browser menu → **Add to Home screen**. iPhone: Safari Share → **Add to Home Screen**. This is a mobile-friendly website; no native APK/iOS app or PWA manifest/service worker has been built.

## Current workflow
- Customer: register → search real worker profiles → submit request → see request history → cancel a pending request.
- Worker: register → edit profile → upload image → receive requests → accept/reject → mark in progress/completed.
- Admin: create account with `create_admin.py` → view basic counts → activate/deactivate worker profiles.
- Assistant: deterministic FAQ helper; it is not a live AI model and needs no API key.

## Security notes
Passwords are hashed using PBKDF2-HMAC-SHA256 with a per-password random salt. SQLAlchemy parameterizes database operations. Production deployment still requires HTTPS, secret management, database backups, rate limiting, stronger audit/monitoring, privacy/terms review, and a professional security review before handling sensitive personal data.
