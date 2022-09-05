"""CardListChange removed

Revision ID: 71596b73b569
Revises: 6b5270ecfcaa
Create Date: 2022-09-05 07:42:35.529675

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71596b73b569'
down_revision = '6b5270ecfcaa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('card_list_assignment')
    with op.batch_alter_table('card_activity', schema=None) as batch_op:
        batch_op.add_column(sa.Column('changes', sa.Text(), nullable=True))

    with op.batch_alter_table('card_checklist', schema=None) as batch_op:
        batch_op.add_column(sa.Column('card_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'card', ['card_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('card_checklist', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('card_id')

    with op.batch_alter_table('card_activity', schema=None) as batch_op:
        batch_op.drop_column('changes')

    op.create_table('card_list_assignment',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('activity_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('from_list_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('to_list_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['activity_id'], ['card_activity.id'], name='card_list_assignment_activity_id_fkey'),
    sa.ForeignKeyConstraint(['from_list_id'], ['list.id'], name='card_list_assignment_from_list_id_fkey'),
    sa.ForeignKeyConstraint(['to_list_id'], ['list.id'], name='card_list_assignment_to_list_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='card_list_assignment_pkey')
    )
    # ### end Alembic commands ###
