"""Display verified local demo admin credentials, regardless of working folder."""
import json
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"


def get_admin_credentials(backend=BACKEND):
    backend = Path(backend)
    credentials = backend / ".demo-accounts.json"
    database = backend / "storymap.db"
    if not credentials.is_file():
        raise RuntimeError(
            "The local demo login file has not been created. Run SetupDemo.bat and wait "
            "for 'Setup complete'. If setup says 'Existing database preserved', keep "
            "that database and use a fresh clone for the supplied demo accounts."
        )
    if not database.is_file():
        raise RuntimeError("The local database is missing. Run SetupDemo.bat before opening the app.")
    try:
        accounts = json.loads(credentials.read_text(encoding="utf-8"))["accounts"]
        admin = next(account for account in accounts if account.get("role") == "admin")
        email, password = admin["email"], admin["password"]
        if not isinstance(email, str) or not isinstance(password, str) or not email or not password:
            raise ValueError("Empty account field")
    except (ValueError, KeyError, TypeError, StopIteration) as exc:
        raise RuntimeError("The local demo login file is invalid. Keep it for troubleshooting; use a fresh clone for the demo.") from exc
    try:
        from pwdlib import PasswordHash
    except ImportError as exc:
        raise RuntimeError("Python dependencies are missing. Run SetupDemo.bat first.") from exc
    try:
        with closing(sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True)) as db:
            row = db.execute(
                "SELECT password_hash, role, is_active FROM users WHERE email = ?", (email,)
            ).fetchone()
    except sqlite3.Error as exc:
        raise RuntimeError("The local database could not be read. Close the app, then run SetupDemo.bat and read any error shown.") from exc
    matches = False
    if row and row[1] == "admin" and row[2]:
        try:
            matches = PasswordHash.recommended().verify(password, row[0])
        except Exception:
            pass
    if not matches:
        raise RuntimeError(
            "These saved demo credentials do not match an active admin in this database. "
            "No accounts or stories were changed. Keep this installation and use a fresh clone for the supplied demo."
        )
    return email, password


def main():
    try:
        email, password = get_admin_credentials()
    except (OSError, RuntimeError) as exc:
        print(f"Admin login unavailable: {exc}", file=sys.stderr)
        return 1
    print("This login was checked against this folder's local database.")
    print("Keep these details private and do not include this window in the video.")
    print()
    print(f"ADMIN EMAIL:    {email}")
    print(f"ADMIN PASSWORD: {password}")
    print()
    print("Open http://127.0.0.1:3000/login and copy the email and password above.")
    print("If another account is signed in, log out first or use a private browser window.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
