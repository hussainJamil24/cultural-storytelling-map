"""hash existing user passwords

Revision ID: 108551412bc6
Revises: 056d2815108c
Create Date: 2026-06-15 15:12:08.510053

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '108551412bc6'
down_revision: Union[str, Sequence[str], None] = '056d2815108c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Replace any plaintext password with a bcrypt hash."""
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    bind = op.get_bind()
    rows = bind.execute(sa.text("SELECT id, password FROM users")).fetchall()
    for user_id, password in rows:
        # skip empty values and anything already hashed (idempotent / safe to re-run)
        if not password or password.startswith("$2"):
            continue
        hashed = pwd_context.hash(password)
        bind.execute(
            sa.text("UPDATE users SET password = :pw WHERE id = :id"),
            {"pw": hashed, "id": user_id},
        )


def downgrade() -> None:
    """Irreversible: a bcrypt hash cannot be converted back to plaintext."""
    pass
