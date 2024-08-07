"""instance_assigned_to

Revision ID: 7cefa57c0a76
Revises: 69f9c9a434ba
Create Date: 2024-07-02 21:00:33.158779

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7cefa57c0a76'
down_revision = '69f9c9a434ba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shift_instance', schema=None) as batch_op:
        batch_op.add_column(sa.Column('instance_assigned_to', sa.String(length=128), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shift_instance', schema=None) as batch_op:
        batch_op.drop_column('instance_assigned_to')

    # ### end Alembic commands ###
