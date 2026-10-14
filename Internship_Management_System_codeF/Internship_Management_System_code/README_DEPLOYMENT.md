# Internship Management System — setup and deployment

## Run locally (Windows PowerShell)

1. Install Python 3.10+ and MySQL 8+.
2. In MySQL Workbench, create/select the `internship_management` database and import `database/internship_management.sql`.
3. Copy `.env.example` to `.env`, then fill in your local MySQL password and a private `SECRET_KEY`. Never share the `.env` file.
4. Open PowerShell in this project folder and run:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

5. Start the app with `python backend\app.py`, then open `http://127.0.0.1:5000`.

The app automatically loads a local `.env` file through `python-dotenv`. Hosted services should use their environment-variable dashboard instead.

## Deploy on Render + hosted MySQL

1. Create a hosted MySQL database (for example, Aiven) and import `database/internship_management.sql` into it.
2. Push this project to a **private** GitHub repository. Do not commit `.env`, passwords, or database exports containing real student data.
3. In Render, create a Web Service from the repository. The included `render.yaml` describes the service; alternatively use build command `pip install -r requirements.txt` and start command `gunicorn --chdir backend app:app`.
4. In Render's environment settings, set `SECRET_KEY` to a long random value, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME`. Use the exact host/user/password/database details from your MySQL provider. If the provider requires TLS, set `DB_SSL_CA` to the CA certificate path available to the service; the connector enables certificate verification when this variable is set.
5. Ensure the database allows connections from the web service and is not publicly open to everyone.
6. Deploy, then test `/`, `/register`, `/login`, `/opportunities`, `/admin/login`, and admin CRUD functions.

## Important security notes

- Change any database password that was previously hard-coded in a project ZIP or shared with anyone. This package no longer contains the old password.
- The default admin credentials (`admin` / `admin123`) are for local development only. Set strong values in the hosting environment before deployment.
- This is a student project baseline, not a security audit. Test all workflows against a staging database before sharing the URL with your instructor.
