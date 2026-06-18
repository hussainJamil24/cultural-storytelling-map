import sqlite3
import sys
from pathlib import Path

db = Path(__file__).resolve().parent / "storymap.db"
story_id = int(sys.argv[1]) if len(sys.argv) > 1 else 2

conn = sqlite3.connect(db)
row = conn.execute("select id, title from stories where id=?", (story_id,)).fetchone()
if row is None:
    print(f"No story with id {story_id}")
    raise SystemExit(0)

print(f"Deleting story {row[0]}: {row[1]!r}")
c = conn.execute("delete from comments where story_id=?", (story_id,)).rowcount
l = conn.execute("delete from likes where story_id=?", (story_id,)).rowcount
s = conn.execute("delete from stories where id=?", (story_id,)).rowcount
conn.commit()
conn.close()
print(f"deleted -> story rows: {s}, comments: {c}, likes: {l}")
