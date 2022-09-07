"""empty message

Revision ID: 465f11749bac
Revises: 2a8ee65ccf68
Create Date: 2022-09-12 21:27:54.005889

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '465f11749bac'
down_revision = '2a8ee65ccf68'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('messages', sa.Column('message_type', sa.String(), nullable=False))
    op.add_column('messages', sa.Column('scheduler_task_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_messages_scheduler_task_id'), 'messages', ['scheduler_task_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_messages_scheduler_task_id'), table_name='messages')
    op.drop_column('messages', 'scheduler_task_id')
    op.drop_column('messages', 'message_type')
    # ### end Alembic commands ###
