"""seeking_replacement

Revision ID: ad64013c0042
Revises: cc572f17abe9
Create Date: 2024-06-19 11:08:31.753544

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad64013c0042'
down_revision = 'cc572f17abe9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shift', schema=None) as batch_op:
        batch_op.add_column(sa.Column('seeking_replacement', sa.Boolean(), nullable=False, default=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shift', schema=None) as batch_op:
        batch_op.drop_column('seeking_replacement')

    # ### end Alembic commands ###
