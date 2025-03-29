"""Update account model

Revision ID: 9c6ebc6096ae
Revises: 
Create Date: 2025-03-29 11:33:58.209485

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c6ebc6096ae'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=250), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('oauth_sub', sa.String(length=250), nullable=False),
    sa.Column('nessie_customer_id', sa.String(length=250), nullable=True),
    sa.Column('plaid_access_token', sa.String(length=250), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('accounts',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('nessie_id', sa.String(length=250), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nessie_id')
    )
    op.create_table('merchants',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=250), nullable=False),
    sa.Column('category_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transactions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('type', sa.Enum('DEBIT', 'CREDIT', name='transactiontype'), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('account_id', sa.UUID(), nullable=False),
    sa.Column('merchant_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
    sa.ForeignKeyConstraint(['merchant_id'], ['merchants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transactions')
    op.drop_table('merchants')
    op.drop_table('accounts')
    op.drop_table('users')
    op.drop_table('categories')
    # ### end Alembic commands ###
