🏡 Daily Ease

Local Help. Trusted People. Easier Everyday Living.

Daily Ease is a student-built web application concept for connecting people in villages, small towns, and neighbourhoods with local service providers. The goal is to make everyday help—such as plumbing, electrical repairs, cleaning, tutoring, and cooking—easier to discover through a simple, approachable platform.

Project status: Student MVP / demonstration project. Some workflows are implemented, but this is not yet a fully audited production marketplace. Please read the limitations below before relying on it for real services.

🌐 **Live Website:** [Visit Daily Ease](https://daily-ease-npgrq4uguomghtcbl6owmr.streamlit.app/)


👋 For visitors

Daily Ease explores how technology can help communities find local skills in one place.

What you can explore

Discover services: Search worker profiles by service, category, and locality.

Worker profiles: View skills, experience, indicative pricing, availability, and profile information.

Customer accounts: Register and sign in to use account-based features.

Become a worker: Create a worker account and maintain a service profile.

Service requests: Submit requests to eligible, non-demo worker profiles and follow request status.

Three interface languages: English, हिन्दी, and Hinglish options are available.

Daily Ease Assistant: An in-app FAQ helper for common usage questions.

Admin area: A basic protected dashboard for platform statistics and worker activation controls.

Demo profiles are sample data for exploring the interface. They are not real people, not verified providers, and cannot receive bookings.

🎓 For students and evaluators

Daily Ease is a practical example of a small full-stack Python project. It brings together a web UI, relational database access, authentication, role-based workflows, localization, and automated tests.

Learning objectives

Build an interactive web interface with Streamlit.

Organize application code into reusable Python modules.

Model users, worker profiles, and service requests with SQLAlchemy.

Hash passwords instead of storing them as plain text.

Implement basic role-aware actions and request status transitions.

Add English, Hindi, and Hinglish interface strings.

Write automated tests with pytest.

Prepare a Python application for GitHub and hosted deployment.

Technology stack

Technology

Purpose

Python

Main application language

Streamlit

Web interface

SQLAlchemy

Database models and operations

SQLite

Local development and tests

PostgreSQL

Optional persistent production database

Pillow

Worker image processing

Pandas

Data handling dependency

Pytest

Automated tests

🧭 How the app works

A visitor explores service categories and worker profiles.

A customer creates an account and signs in.

The customer searches for an eligible worker and submits a service request.

The worker reviews the request and can accept or reject it, then update its status when permitted.

Users can revisit the app to check request status and access the help assistant.

The exact options available depend on the account role and whether a profile is a demo record.

🚀 Run the project locally

1. Requirements

Python 3.11 or a compatible newer version

Git (optional, for cloning the repository)

2. Get the source code

Clone the repository:

git clone https://github.com/Engineer9336/daily-ease.git
cd daily-ease

Or download the repository as a ZIP from GitHub and extract it.

3. Create a virtual environment

Windows PowerShell:

python -m venv .venv
.venv\Scripts\Activate.ps1

macOS / Linux:

python3 -m venv .venv
source .venv/bin/activate

4. Install dependencies

python -m pip install -r requirements.txt

5. Start the application

streamlit run app.py

Streamlit will print a local address in the terminal. Open that address in your browser. On the first run, the app initializes its database and adds clearly labelled demo data.

🧪 Run automated tests

With the virtual environment active, run:

pytest -q

Tests are intended to cover selected core behaviour, including password hashing and login, duplicate registration, worker search, request status transitions and permissions, translation-key coverage, and profile authorization. A passing test suite does not replace end-to-end browser testing or a security audit.

🔐 Creating an administrator account locally

For local development, stop the app and run:

python create_admin.py

Follow the prompts to create or promote an administrator account, then restart the app and sign in. Use a private password and never commit credentials, .env files, or secrets to GitHub. For a hosted instance, follow the deployment provider's secure configuration process and do not expose admin credentials publicly.

⚠️ Current limitations

This project is an MVP intended for learning and demonstration. The following should not be assumed to be available:

Payments: No real payment gateway or transaction processing is implemented.

Identity verification: Worker profiles are not automatically identity-verified. Do not treat an “unverified” profile as trusted solely because it appears in the app.

Demo bookings: Sample/demo profiles cannot receive service requests.

Persistent image storage: Local uploads may not survive redeployments or ephemeral hosting. Durable object storage must be configured for production use.

Production database: SQLite is suitable for local development. A hosted deployment that needs durable data should use a properly configured persistent PostgreSQL database.

Notifications and support: SMS/OTP, email notifications, and a staffed customer-support channel are not configured.

Admin tools: The dashboard is basic; a full verification review, category-management, complaints-management, and activity-log workflow is not complete.

Localization: English, Hindi, and Hinglish are supported by the translation module, but some technical errors or less-used labels may still appear in English.

Mobile app: This is a mobile-friendly website, not a native Android APK or iOS app. A PWA manifest/service worker is not included.

Security and legal review: The project has not undergone a professional security audit or legal/privacy compliance review.

Please do not enter sensitive personal information or use this demonstration as the sole basis for hiring a service provider.

🌱 Possible future improvements

Ideas for students who want to extend the project:

Add real worker verification with a documented review process.

Integrate a secure payment provider in a test environment before production use.

Add ratings, reviews, complaint reporting, and moderation workflows.

Add email/SMS notifications and booking reminders.

Use persistent object storage for worker photos.

Add database migrations and scheduled backups.

Improve localization coverage and accessibility testing.

Add automated browser tests and test mobile/desktop layouts.

Add monitoring, rate limiting, and a more complete security review.

🤝 Contributing / learning from the project

Students can explore the modules, run the tests, report bugs, and propose improvements. Before submitting changes, run the app locally and execute pytest -q. Avoid committing credentials, private user information, uploaded personal photos, or database files containing real data.

📄 Project information

Project: Daily Ease

Tagline: Local Help. Trusted People. Easier Everyday Living.

Repository: Engineer9336/daily-ease

Application framework: Streamlit

Intended audience: Visitors, students, project reviewers, and developers learning full-stack Python

Built as a learning-focused MVP exploring how digital tools could make local services easier to discover.
