import sqlite3
import sys
from pathlib import Path

db = Path(__file__).resolve().parent / "storymap.db"

# Emails passed on the command line, e.g.:
#   python promote_admin.py a@gmail.com b@gmail.com
# If none are given, falls back to this default list.
emails = sys.argv[1:] or [
    "admin@gmail.com",
]

conn = sqlite3.connect(db)
for email in emails:
    n = conn.execute("update users set role='admin' where email=?", (email,)).rowcount
    print(f"{email}: rows updated {n}")
conn.commit()
conn.close()
