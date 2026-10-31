"""add enquiry conversion tracking

Revision ID: 2e3b1bebff15
Revises: 782c3b664968
Create Date: 2026-09-21 14:45:59.162360

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e3b1bebff15'
down_revision = '782c3b664968'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('enquiries', schema=None) as batch_op:
        batch_op.add_column(sa.Column('converted_order_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('converted_at', sa.DateTime(), nullable=True))
        batch_op.create_index(
            batch_op.f('ix_enquiries_converted_order_id'), ['converted_order_id'], unique=False
        )
        batch_op.create_foreign_key(
            'fk_enquiries_converted_order_id_orders',
            'orders', ['converted_order_id'], ['id'], ondelete='SET NULL'
        )


def downgrade():
    with op.batch_alter_table('enquiries', schema=None) as batch_op:
        batch_op.drop_constraint('fk_enquiries_converted_order_id_orders', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_enquiries_converted_order_id'))
        batch_op.drop_column('converted_at')
        batch_op.drop_column('converted_order_id')
