"""Add description field to Account model

Revision ID: 384bd6a3d190
Revises: bc80e1afec93
Create Date: 2025-04-17 08:50:35.372028

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '384bd6a3d190'
down_revision = 'bc80e1afec93'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.String(length=200), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.drop_column('description')

    # ### end Alembic commands ###
