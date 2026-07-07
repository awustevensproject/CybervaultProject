# CyberVault

Pre-College Cyber Vault — secure login system with Flask.

## Run in browser (development)

```bash
cd cybervault
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5001](http://127.0.0.1:5001)

## Run as a desktop app (recommended)

```bash
source .venv/bin/activate
pip install -r requirements.txt
python run_app.py
```

Or **double-click** `CyberVault.command` in Finder.

This opens a native 600×600 window — no browser tab needed.

## Test accounts

| Email | Password |
|-------|----------|
| admin@cybervault.local | admin123 |
| student@cybervault.local | pass |

## Project structure

```
cybervault/
├── app.py              # Flask routes
├── run_app.py          # Native desktop launcher
├── CyberVault.command  # Double-click to run (Mac)
├── auth/               # Login & signup logic
├── database/           # User storage (in-memory for now)
├── templates/          # Apple-style dark UI
├── utils/              # Hashing & security logging
└── logs/security.log   # Auth event log
```
