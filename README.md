# CyberVault

Login system with Flask and Supabase.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` with your Supabase URL and service role key. Run `supabase/users_table.sql` in the Supabase SQL Editor.

Generate a `SECRET_KEY`:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Run

```bash
python app.py
```

Open http://127.0.0.1:5001

Native window:

```bash
python run_app.py
```

## Local test accounts

Only work if Supabase is not configured in `.env`:

| Username | Password |
|----------|----------|
| admin | Admin1234 |
| student | Student123 |

## Security

- Bcrypt password hashing
- zxcvbn password strength scoring (live meter + signup validation)
- Have I Been Pwned breach check on signup
- Rate limiting on login and signup
- Security log at `logs/security.log`
- Login required for dashboard and admin pages
- Supabase RLS on the users table

Do not commit `.env`. Use `.env.example` for placeholders only.
