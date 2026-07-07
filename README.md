# CyberVault

Pre-College Cyber Vault — login system with Flask and Supabase.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Supabase URL and service role key to `.env`, then run `supabase/users_table.sql` in the Supabase SQL Editor.

Generate a strong `SECRET_KEY` before deploying:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Run

```bash
python app.py
```

Desktop app: `python run_app.py`

## Local dev without Supabase

| Username | Password |
|----------|----------|
| admin    | Admin1234 |
| student  | Student123 |

## Security

**Included:** bcrypt passwords, rate limiting, local audit log (`logs/security.log`), login/role guards, RLS on Supabase tables, service-role-only DB access, HTTP-only session cookies, session reset on login.

**Not production-hardened yet:** set `SESSION_COOKIE_SECURE=true` behind HTTPS, use a strong `SECRET_KEY`, turn off `FLASK_DEBUG`, and deploy behind a real host. No MFA or CSRF tokens yet.
