import sqlite3
from pathlib import Path

db = Path(__file__).resolve().parent / "storymap.db"
emails = [
    "admin@gmail.com",
    # "second@gmail.com",
    # "third@gmail.com",
]

conn = sqlite3.connect(db)
for email in emails:
    n = conn.execute("update users set role='admin' where email=?", (email,)).rowcount
    print(f"{email}: rows updated {n}")
conn.commit()
for row in conn.execute("select id, name, email, role from users"):
    print(row)
conn.close()
