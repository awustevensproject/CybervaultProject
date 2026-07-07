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

- Bcrypt password hashing (unique salt per password)
- CSRF tokens on all POST forms and the strength API
- zxcvbn password strength scoring (live meter + signup validation)
- Have I Been Pwned breach check on signup (fail-closed if unavailable)
- Rate limiting on login, signup, and password-strength API
- Security log at `logs/security.log` (local only, IPs stored as hashes)
- Session cookies: HttpOnly, SameSite=Lax, 8-hour lifetime
- Security headers (CSP, X-Frame-Options, nosniff)
- Admin role re-checked from database on each request

Do not commit `.env`. Use `.env.example` for placeholders only.
