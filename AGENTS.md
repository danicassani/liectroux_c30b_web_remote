# Repository workflow

For each new task, create a new branch and create a pull request at the end, as requested by the owner. Preserve existing user changes. Never commit device keys, device IDs, private captures or Tuya credentials.

Use Python 3.12, install requirements.lock in .venv, and run `DJANGO_DEBUG=1 ROBOT_DEMO=1 .venv/bin/python manage.py test` after behavior changes. Use demo mode for validation; do not send commands to a physical robot without explicit authorization. The DPS evidence and unknowns are documented in docs/dps.md.
