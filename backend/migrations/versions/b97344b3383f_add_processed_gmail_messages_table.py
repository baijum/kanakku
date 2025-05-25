"""add_processed_gmail_messages_table

Revision ID: b97344b3383f
Revises: dc70cfcfbace
Create Date: 2025-05-25 15:34:57.466131

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b97344b3383f"
down_revision = "dc70cfcfbace"
branch_labels = None
depends_on = None


def upgrade():
    # Create processed_gmail_messages table
    op.create_table(
        "processed_gmail_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("gmail_message_id", sa.String(length=255), nullable=False),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "gmail_message_id", name="uq_user_gmail_message"
        ),
    )


def downgrade():
    # Drop processed_gmail_messages table
    op.drop_table("processed_gmail_messages")
