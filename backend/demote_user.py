import sqlite3
import sys
from pathlib import Path

db = Path(__file__).resolve().parent / "storymap.db"

# Emails passed on the command line, e.g.:
#   python demote_user.py a@gmail.com b@gmail.com
emails = sys.argv[1:]
if not emails:
    print("Usage: python demote_user.py <email> [more emails...]")
    raise SystemExit(1)

conn = sqlite3.connect(db)
for email in emails:
    n = conn.execute("update users set role='user' where email=?", (email,)).rowcount
    print(f"{email}: rows updated {n}")
conn.commit()
conn.close()
