"""Configure a local demo without echoing or committing secrets."""
import getpass
import os
import secrets
from pathlib import Path
from dotenv import dotenv_values, set_key

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / "backend" / ".env"


def main():
    values = dotenv_values(ENV) if ENV.exists() else {}
    key = values.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY", "")
    if not key:
        key = getpass.getpass("Paste the Gemini API key from Charalampos (hidden), then press Enter: ").strip()
    if not key:
        raise SystemExit("A Gemini key is required for this demo. Run SetupDemo.bat again with the private key.")
    ENV.touch(exist_ok=True)
    set_key(str(ENV), "GEMINI_API_KEY", key)
    set_key(str(ENV), "GEMINI_MODEL", values.get("GEMINI_MODEL") or "gemini-flash-lite-latest")
    set_key(str(ENV), "NARRIFY_AUTO_APPROVE", "false")
    set_key(str(ENV), "JWT_SECRET_KEY", values.get("JWT_SECRET_KEY") or secrets.token_urlsafe(48))
    print("Private backend settings saved. Autoapproval is OFF.")


if __name__ == "__main__":
    main()
