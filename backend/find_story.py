import sqlite3
from pathlib import Path

db = Path(__file__).resolve().parent / "storymap.db"
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
for r in conn.execute("select id, title, image_url, status from stories"):
    print(dict(r))
conn.close()
