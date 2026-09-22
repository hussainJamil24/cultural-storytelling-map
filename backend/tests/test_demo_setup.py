import hashlib
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from pwdlib import PasswordHash
from sqlalchemy import create_engine

from app.db.session import init_db
from demo_setup import BACKEND_DIR, TABLES, bootstrap


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DemoSetupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.backend = Path(self.temporary.name) / "backend"
        self.backend.mkdir()
        self.database = self.backend / "storymap.db"
        self.credentials = self.backend / ".demo-accounts.json"

    def tearDown(self):
        self.temporary.cleanup()

    def test_complete_snapshot_and_second_run_preserve_live_edits(self):
        snapshot = json.loads((BACKEND_DIR / "demo/snapshot.json").read_text(encoding="utf-8"))
        result = bootstrap(self.backend)
        self.assertEqual(result["status"], "demo_initialized")
        self.assertEqual(result["counts"], {table: len(snapshot[table]) for table in TABLES})
        accounts = json.loads(self.credentials.read_text(encoding="utf-8"))["accounts"]
        account_by_id = {row["id"]: row for row in accounts}
        self.assertEqual(len(accounts), len(snapshot["users"]))
        with closing(sqlite3.connect(self.database)) as connection, connection:
            connection.row_factory = sqlite3.Row
            for table in TABLES:
                restored = [dict(row) for row in connection.execute(f'SELECT * FROM "{table}" ORDER BY id')]
                if table == "users":
                    for row in restored:
                        hashed = row.pop("password_hash")
                        self.assertTrue(PasswordHash.recommended().verify(account_by_id[row["id"]]["password"], hashed))
                self.assertEqual(restored, snapshot[table])
            connection.execute("UPDATE stories SET content = 'A later local edit' WHERE id = 1")
            connection.execute("UPDATE stories SET status = 'pending' WHERE id = 17")
        database_digest = digest(self.database)
        credentials_digest = digest(self.credentials)
        result = bootstrap(self.backend)
        self.assertEqual(result["status"], "existing_database_preserved")
        self.assertEqual(result["story_status_counts"]["pending"], 1)
        self.assertEqual(digest(self.database), database_digest)
        self.assertEqual(digest(self.credentials), credentials_digest)

    def test_incompatible_schema_fails_before_any_schema_or_data_write(self):
        with closing(sqlite3.connect(self.database)) as connection, connection:
            connection.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
            connection.execute("INSERT INTO users VALUES (1, 'Existing account')")
        before = digest(self.database)
        with self.assertRaisesRegex(RuntimeError, "Database schema is incompatible"):
            bootstrap(self.backend)
        self.assertEqual(digest(self.database), before)
        self.assertFalse(self.credentials.exists())
        self.assertFalse((self.backend / "uploads").exists())
        db_engine = create_engine(f"sqlite:///{self.database.as_posix()}")
        try:
            with self.assertRaisesRegex(RuntimeError, "no tables or data were changed"):
                init_db(db_engine)
        finally:
            db_engine.dispose()
        self.assertEqual(digest(self.database), before)
        with closing(sqlite3.connect(self.database)) as connection, connection:
            self.assertEqual(connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall(), [("users",)])

    def test_non_demo_user_and_credentials_are_preserved(self):
        db_engine = create_engine(f"sqlite:///{self.database.as_posix()}")
        try:
            init_db(db_engine)
        finally:
            db_engine.dispose()
        with closing(sqlite3.connect(self.database)) as connection, connection:
            connection.execute(
                "INSERT INTO users (id, name, email, password_hash, role, is_active, created_at) "
                "VALUES (200, 'Existing account', 'existing@example.invalid', 'existing-hash', 'user', 1, '2026-01-01')"
            )
        before = digest(self.database)
        result = bootstrap(self.backend)
        self.assertEqual(result["status"], "existing_database_preserved")
        self.assertEqual(result["counts"]["users"], 1)
        self.assertEqual(result["counts"]["stories"], 0)
        self.assertEqual(digest(self.database), before)
        self.assertFalse(self.credentials.exists())

    def test_existing_different_media_is_not_overwritten(self):
        upload = self.backend / "uploads/syrian.jpg"
        upload.parent.mkdir()
        upload.write_bytes(b"existing different media")
        with self.assertRaisesRegex(RuntimeError, "Existing media differs and was preserved"):
            bootstrap(self.backend)
        self.assertEqual(upload.read_bytes(), b"existing different media")
        self.assertFalse(self.database.exists())
        self.assertFalse(self.credentials.exists())

    def test_tampered_snapshot_is_rejected_before_database_creation(self):
        demo = Path(self.temporary.name) / "tampered-demo"
        demo.mkdir()
        (demo / "manifest.json").write_bytes((BACKEND_DIR / "demo/manifest.json").read_bytes())
        (demo / "snapshot.json").write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "snapshot checksum mismatch"):
            bootstrap(self.backend, demo)
        self.assertFalse(self.database.exists())


if __name__ == "__main__":
    unittest.main()
