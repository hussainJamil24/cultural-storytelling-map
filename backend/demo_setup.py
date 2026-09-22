"""Install the reviewed demo snapshot once, without replacing existing data."""

import hashlib
import json
import secrets
import sqlite3
import sys
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from pwdlib import PasswordHash
from sqlalchemy import create_engine

from app.db.session import init_db, validate_existing_schema
# Register every table before checking or creating the schema.
from app.models import comment_model, like_model, story_model, user_model  # noqa: F401


BACKEND_DIR = Path(__file__).resolve().parent
TABLES = ("users", "stories", "story_translations", "comments", "likes")


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _quote_identifier(name):
    return '"' + name.replace('"', '""') + '"'


def _has_data(connection):
    tables = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' "
        "AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    return any(
        connection.execute(f"SELECT 1 FROM {_quote_identifier(name)} LIMIT 1").fetchone()
        for (name,) in tables
    )


def _database_summary(connection):
    names = {
        row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    counts = {
        name: connection.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
        for name in TABLES if name in names
    }
    statuses = dict(connection.execute(
        "SELECT status, COUNT(*) FROM stories GROUP BY status"
    )) if "stories" in names else {}
    return {"counts": counts, "story_status_counts": statuses}


def _load_bundle(demo_dir, backend_dir):
    manifest = json.loads((demo_dir / "manifest.json").read_text(encoding="utf-8"))
    snapshot_path = demo_dir / "snapshot.json"
    if manifest.get("format_version") != 1:
        raise RuntimeError("Unsupported demo manifest format.")
    if _sha256(snapshot_path) != manifest["snapshot_sha256"]:
        raise RuntimeError("Demo snapshot checksum mismatch; no data was imported.")
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    if set(snapshot) != set(TABLES):
        raise RuntimeError("Demo snapshot table list is invalid.")
    if {name: len(snapshot[name]) for name in TABLES} != manifest["counts"]:
        raise RuntimeError("Demo snapshot counts do not match its manifest.")
    for user in snapshot["users"]:
        expected_email = (
            "admin@demo.narrify.local" if user["role"] == "admin"
            else f'user{user["id"]}@demo.narrify.local'
        )
        if "password_hash" in user or user["email"] != expected_email:
            raise RuntimeError("Demo snapshot contains non-demo account data.")
    copies = []
    for entry in manifest["media"]:
        relative = Path(entry["path"])
        if relative.is_absolute() or len(relative.parts) != 2 or relative.parts[0] != "uploads" or ".." in relative.parts:
            raise RuntimeError("Invalid bundled media path.")
        source = demo_dir / relative
        target = backend_dir / relative
        if not source.is_file() or source.stat().st_size != entry["bytes"] or _sha256(source) != entry["sha256"]:
            raise RuntimeError(f"Bundled media checksum mismatch: {relative}")
        if target.exists() and (not target.is_file() or _sha256(target) != entry["sha256"]):
            raise RuntimeError(f"Existing media differs and was preserved: {target}")
        if not target.exists():
            copies.append((source, target))
    return snapshot, manifest, copies


def bootstrap(backend_dir=BACKEND_DIR, demo_dir=None):
    """Return setup counts; existing populated databases are never reseeded."""
    backend_dir = Path(backend_dir).resolve()
    demo_dir = Path(demo_dir).resolve() if demo_dir is not None else BACKEND_DIR / "demo"
    snapshot, manifest, copies = _load_bundle(demo_dir, backend_dir)
    backend_dir.mkdir(parents=True, exist_ok=True)
    database_path = backend_dir / "storymap.db"
    credentials_path = backend_dir / ".demo-accounts.json"
    db_engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    try:
        # Validation happens before missing tables are created or media is copied.
        validate_existing_schema(db_engine)
        with closing(sqlite3.connect(database_path)) as connection, connection:
            if _has_data(connection):
                return {
                    "status": "existing_database_preserved",
                    **_database_summary(connection),
                    "credentials_path": str(credentials_path) if credentials_path.exists() else None,
                    "missing_media_count": len(manifest["missing_media"]),
                }
        if credentials_path.exists():
            raise RuntimeError(
                f"Existing credentials were preserved: {credentials_path}. "
                "An empty database cannot be initialized over an existing credentials file."
            )
        init_db(db_engine)
        for source, target in copies:
            target.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation prevents replacing a file created since validation.
            with target.open("xb") as destination:
                destination.write(source.read_bytes())
        hasher = PasswordHash.recommended()
        accounts = []
        rows = {name: [dict(row) for row in snapshot[name]] for name in TABLES}
        for user in rows["users"]:
            password = secrets.token_urlsafe(18)
            user["password_hash"] = hasher.hash(password)
            accounts.append({
                "id": user["id"], "name": user["name"], "email": user["email"],
                "role": user["role"], "password": password,
            })
        credentials_written = False
        try:
            with closing(sqlite3.connect(database_path)) as connection, connection:
                connection.execute("PRAGMA foreign_keys = ON")
                connection.execute("BEGIN IMMEDIATE")
                if _has_data(connection):
                    raise RuntimeError("Database was populated during setup; its data was preserved.")
                for table in TABLES:
                    for row in rows[table]:
                        columns = list(row)
                        column_sql = ", ".join(_quote_identifier(column) for column in columns)
                        placeholders = ", ".join("?" for _ in columns)
                        connection.execute(
                            f'INSERT INTO "{table}" ({column_sql}) VALUES ({placeholders})',
                            [row[column] for column in columns],
                        )
                if connection.execute("PRAGMA foreign_key_check").fetchall():
                    raise RuntimeError("Imported demo relationships failed validation.")
                result = _database_summary(connection)
                if result["counts"] != manifest["counts"] or result["story_status_counts"] != manifest["story_status_counts"]:
                    raise RuntimeError("Imported demo counts failed validation.")
                with credentials_path.open("x", encoding="utf-8") as credentials_file:
                    credentials_written = True
                    json.dump({
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "accounts": accounts,
                    }, credentials_file, ensure_ascii=False, indent=2)
                    credentials_file.write("\n")
                credentials_path.chmod(0o600)
            return {
                "status": "demo_initialized", **result,
                "credentials_path": str(credentials_path),
                "missing_media_count": len(manifest["missing_media"]),
            }
        except Exception:
            if credentials_written:
                credentials_path.unlink(missing_ok=True)
            raise
    finally:
        db_engine.dispose()


def main():
    try:
        result = bootstrap()
    except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
        print(f"Demo setup stopped: {exc}", file=sys.stderr)
        return 1
    print(result["status"].replace("_", " ").capitalize() + ".")
    print("Data: " + ", ".join(f"{count} {table}" for table, count in result["counts"].items()))
    print("Stories: " + ", ".join(f"{count} {status}" for status, count in result["story_status_counts"].items()))
    if result["credentials_path"]:
        print(f'Local account credentials: {result["credentials_path"]}')
    if result["missing_media_count"]:
        print(f'{result["missing_media_count"]} pre-existing missing media references are documented in demo/manifest.json.')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
