"""no_people

Revision ID: cc572f17abe9
Revises: 0d056e0438e6
Create Date: 2024-05-27 21:45:29.722610

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc572f17abe9'
down_revision = '0d056e0438e6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shift', schema=None) as batch_op:
        batch_op.add_column(sa.Column('assigned_to', sa.String(length=32), nullable=True))
        batch_op.drop_constraint('fk_shift_person_id', type_='foreignkey')
        batch_op.drop_column('person_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shift', schema=None) as batch_op:
        batch_op.add_column(sa.Column('person_id', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key('fk_shift_person_id', 'person', ['person_id'], ['person_id'])
        batch_op.drop_column('assigned_to')

    # ### end Alembic commands ###
