"""fixed rlations between messages and message photos

Revision ID: 0a8739d89c4f
Revises: 26ed21c13c17
Create Date: 2021-12-27 01:04:53.224401

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0a8739d89c4f'
down_revision = '26ed21c13c17'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('message_photos_message_id_fkey', 'message_photos', type_='foreignkey')
    op.create_foreign_key(None, 'message_photos', 'messages', ['message_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'message_photos', type_='foreignkey')
    op.create_foreign_key('message_photos_message_id_fkey', 'message_photos', 'chat_rooms', ['message_id'], ['id'])
    # ### end Alembic commands ###
