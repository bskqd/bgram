"""add chat rooms photos

Revision ID: 9739f572c668
Revises: 9b302200ddb2
Create Date: 2021-12-01 23:20:39.620481

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '9739f572c668'
down_revision = '9b302200ddb2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'chat_rooms_photos',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('modified_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.Column('chat_room_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['chat_room_id'],
            ['chat_rooms.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('file_path'),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('chat_rooms_photos')
    # ### end Alembic commands ###
