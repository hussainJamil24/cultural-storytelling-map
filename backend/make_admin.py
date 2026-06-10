"""
Promote or demote a user's admin status.

Usage:
    python make_admin.py <email>            # grant admin
    python make_admin.py <email> --remove   # revoke admin

Run from the backend folder so it finds storymap.db.
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "storymap.db"


def main():
    if len(sys.argv) < 2:
        print("Usage: python make_admin.py <email> [--remove]")
        sys.exit(1)

    email = sys.argv[1]
    remove = "--remove" in sys.argv
    new_value = 0 if remove else 1

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # confirm the user exists first
    cur.execute("SELECT id, name, is_admin FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    if user is None:
        print(f"No user found with email: {email}")
        con.close()
        sys.exit(1)

    cur.execute("UPDATE users SET is_admin = ? WHERE email = ?", (new_value, email))
    con.commit()
    con.close()

    action = "removed admin from" if remove else "promoted to admin"
    print(f"Successfully {action}: {user[1]} ({email})")


if __name__ == "__main__":
    main()
