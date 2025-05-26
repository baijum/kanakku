"""add_comprehensive_fts_search_vector

Revision ID: dc70cfcfbace
Revises: a1b2c3d4e5f6
Create Date: 2025-05-24 20:47:27.620159

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "dc70cfcfbace"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    # Add search_vector column to transaction table
    op.add_column(
        "transaction", sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True)
    )

    # Create GIN index for efficient full-text search
    op.create_index(
        "idx_transaction_search_vector",
        "transaction",
        ["search_vector"],
        postgresql_using="gin",
    )

    # Create comprehensive trigger function with status mapping and amount formatting
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_transaction_search_vector() RETURNS TRIGGER AS $$
        DECLARE
            status_text TEXT;
            amount_text TEXT;
            account_name TEXT;
            account_desc TEXT;
        BEGIN
            -- Handle transaction table changes
            IF TG_TABLE_NAME = 'transaction' THEN
                -- Map status symbols to verbose text
                CASE NEW.status
                    WHEN '*' THEN status_text := 'Cleared';
                    WHEN '!' THEN status_text := 'Pending';
                    ELSE status_text := 'Unmarked';
                END CASE;

                -- Format amount as text (handle both integer and decimal amounts)
                amount_text := CASE
                    WHEN NEW.amount = FLOOR(NEW.amount) THEN FLOOR(NEW.amount)::TEXT
                    ELSE NEW.amount::TEXT
                END;

                -- Get account information
                SELECT name, COALESCE(description, '') INTO account_name, account_desc
                FROM account WHERE id = NEW.account_id;

                -- Build comprehensive search vector
                NEW.search_vector = to_tsvector('english',
                    COALESCE(NEW.description, '') || ' ' ||
                    COALESCE(NEW.payee, '') || ' ' ||
                    COALESCE(amount_text, '') || ' ' ||
                    COALESCE(NEW.currency, '') || ' ' ||
                    COALESCE(status_text, '') || ' ' ||
                    COALESCE(account_name, '') || ' ' ||
                    COALESCE(account_desc, '')
                );
                RETURN NEW;
            END IF;

            -- Handle account table changes - update all related transactions
            IF TG_TABLE_NAME = 'account' THEN
                UPDATE transaction
                SET search_vector = to_tsvector('english',
                    COALESCE(description, '') || ' ' ||
                    COALESCE(payee, '') || ' ' ||
                    CASE
                        WHEN amount = FLOOR(amount) THEN FLOOR(amount)::TEXT
                        ELSE amount::TEXT
                    END || ' ' ||
                    COALESCE(currency, '') || ' ' ||
                    CASE status
                        WHEN '*' THEN 'Cleared'
                        WHEN '!' THEN 'Pending'
                        ELSE 'Unmarked'
                    END || ' ' ||
                    COALESCE(NEW.name, '') || ' ' ||
                    COALESCE(NEW.description, '')
                )
                WHERE account_id = NEW.id;
                RETURN NEW;
            END IF;

            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    # Create triggers for both tables
    op.execute(
        """
        CREATE TRIGGER transaction_search_vector_update
            BEFORE INSERT OR UPDATE OF description, payee, amount, currency, status, account_id ON transaction
            FOR EACH ROW EXECUTE FUNCTION update_transaction_search_vector();
    """
    )

    op.execute(
        """
        CREATE TRIGGER account_search_vector_update
            AFTER UPDATE OF name, description ON account
            FOR EACH ROW EXECUTE FUNCTION update_transaction_search_vector();
    """
    )

    # Populate existing records with comprehensive search vectors
    op.execute(
        """
        UPDATE transaction
        SET search_vector = to_tsvector('english',
            COALESCE(description, '') || ' ' ||
            COALESCE(payee, '') || ' ' ||
            CASE
                WHEN amount = FLOOR(amount) THEN FLOOR(amount)::TEXT
                ELSE amount::TEXT
            END || ' ' ||
            COALESCE(currency, '') || ' ' ||
            CASE status
                WHEN '*' THEN 'Cleared'
                WHEN '!' THEN 'Pending'
                ELSE 'Unmarked'
            END || ' ' ||
            COALESCE((SELECT name FROM account WHERE account.id = transaction.account_id), '') || ' ' ||
            COALESCE((SELECT description FROM account WHERE account.id = transaction.account_id), '')
        );
    """
    )


def downgrade():
    # Drop triggers
    op.execute(
        "DROP TRIGGER IF EXISTS transaction_search_vector_update ON transaction;"
    )
    op.execute("DROP TRIGGER IF EXISTS account_search_vector_update ON account;")

    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS update_transaction_search_vector();")

    # Drop index
    op.drop_index("idx_transaction_search_vector", table_name="transaction")

    # Drop column
    op.drop_column("transaction", "search_vector")
