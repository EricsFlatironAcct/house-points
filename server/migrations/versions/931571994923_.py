"""empty message

Revision ID: 931571994923
Revises: 
Create Date: 2023-10-06 20:10:44.375516

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '931571994923'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('family_table',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('family_name', sa.String(), nullable=False),
    sa.Column('family_username', sa.String(), nullable=True),
    sa.Column('_password_hash', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('family_username')
    )
    op.create_table('find_table',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_table',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('head_of_household', sa.Boolean(), nullable=False),
    sa.Column('family_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['family_id'], ['family_table.id'], name=op.f('fk_user_table_family_id_family_table')),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('like_table',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('liking_id', sa.Integer(), nullable=True),
    sa.Column('liked_by_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['liked_by_id'], ['user_table.id'], name=op.f('fk_like_table_liked_by_id_user_table')),
    sa.ForeignKeyConstraint(['liking_id'], ['user_table.id'], name=op.f('fk_like_table_liking_id_user_table')),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('task_table',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('points', sa.Integer(), nullable=True),
    sa.Column('frequency', sa.String(), nullable=True),
    sa.Column('completed_by_user_id', sa.Integer(), nullable=True),
    sa.Column('family_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['completed_by_user_id'], ['user_table.id'], name=op.f('fk_task_table_completed_by_user_id_user_table')),
    sa.ForeignKeyConstraint(['family_id'], ['family_table.id'], name=op.f('fk_task_table_family_id_family_table')),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('task_table')
    op.drop_table('like_table')
    op.drop_table('user_table')
    op.drop_table('find_table')
    op.drop_table('family_table')
    # ### end Alembic commands ###