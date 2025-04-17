"""Remove account type

Revision ID: bc80e1afec93
Revises: 
Create Date: 2025-04-17 08:27:57.148773

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bc80e1afec93"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("account", schema=None) as batch_op:
        batch_op.drop_column("type")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("account", schema=None) as batch_op:
        batch_op.add_column(sa.Column("type", sa.VARCHAR(length=20), nullable=False))

    # ### end Alembic commands ###
