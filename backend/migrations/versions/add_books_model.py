"""add books model

Revision ID: a1b2c3d4e5f6
Revises: previous_revision
Create Date: 2023-07-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime, timezone


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = None  # Set to previous migration if it exists
branch_labels = None
depends_on = None

Base = declarative_base()

# Define models for the migration
class User(Base):
    __tablename__ = 'user'
    id = sa.Column(sa.Integer, primary_key=True)

class Book(Base):
    __tablename__ = 'book'
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), nullable=False)
    name = sa.Column(sa.String(100), nullable=False)
    created_at = sa.Column(sa.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = sa.Column(sa.DateTime, default=lambda: datetime.now(timezone.utc))


def upgrade():
    # Create book table
    op.create_table(
        'book',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'name', name='uq_book_user_name')
    )

    # Add book_id column to account table
    op.add_column('account', sa.Column('book_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_account_book_id', 'account', 'book', ['book_id'], ['id'])
    op.create_unique_constraint('uq_account_book_name', 'account', ['book_id', 'name'])

    # Add book_id column to transaction table
    op.add_column('transaction', sa.Column('book_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_transaction_book_id', 'transaction', 'book', ['book_id'], ['id'])

    # Add active_book_id to user table
    op.add_column('user', sa.Column('active_book_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_user_active_book_id', 'user', 'book', ['active_book_id'], ['id'])

    # Create default books for existing users and migrate data
    bind = op.get_bind()
    session = Session(bind=bind)
    
    try:
        # Get all existing users
        users = session.query(User).all()
        
        # For each user, create a default book
        for user in users:
            default_book = Book(
                user_id=user.id,
                name="Book 1",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            session.add(default_book)
            session.flush()  # Get the ID without committing
            
            # Update the user's active_book_id
            user.active_book_id = default_book.id
            
            # Update account and transaction book_id
            session.execute(
                f"UPDATE account SET book_id = {default_book.id} WHERE user_id = {user.id}"
            )
            session.execute(
                f"UPDATE transaction SET book_id = {default_book.id} WHERE user_id = {user.id}"
            )
        
        session.commit()
        
        # Make book_id columns non-nullable after data migration
        op.alter_column('account', 'book_id', nullable=False)
        op.alter_column('transaction', 'book_id', nullable=False)
        
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def downgrade():
    # Remove foreign key constraints first
    op.drop_constraint('fk_user_active_book_id', 'user', type_='foreignkey')
    op.drop_constraint('fk_transaction_book_id', 'transaction', type_='foreignkey')
    op.drop_constraint('fk_account_book_id', 'account', type_='foreignkey')
    op.drop_constraint('uq_account_book_name', 'account', type_='unique')
    
    # Remove columns
    op.drop_column('user', 'active_book_id')
    op.drop_column('transaction', 'book_id')
    op.drop_column('account', 'book_id')
    
    # Drop book table
    op.drop_table('book') 