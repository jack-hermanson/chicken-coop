"""longer_assigned_to

Revision ID: 69f9c9a434ba
Revises: ad64013c0042
Create Date: 2024-06-24 23:46:18.660393

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '69f9c9a434ba'
down_revision = 'ad64013c0042'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shift', schema=None) as batch_op:
        batch_op.alter_column('assigned_to',
                              existing_type=sa.VARCHAR(length=32),
                              type_=sa.String(length=128),
                              existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shift', schema=None) as batch_op:
        batch_op.alter_column('assigned_to',
                              existing_type=sa.String(length=128),
                              type_=sa.VARCHAR(length=32),
                              existing_nullable=True)

    # ### end Alembic commands ###
