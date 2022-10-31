"""add user photo unique constraint for path

Revision ID: 8c5ad72da78c
Revises: 450d8b17367b
Create Date: 2021-11-01 21:33:38.836149

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '8c5ad72da78c'
down_revision = '450d8b17367b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('uq_file_path', 'users_photos', ['file_path'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uq_file_path', 'users_photos', type_='unique')
    # ### end Alembic commands ###
