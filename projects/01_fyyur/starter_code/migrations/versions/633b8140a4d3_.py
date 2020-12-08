"""empty message

Revision ID: 633b8140a4d3
Revises: 66501d6281ac
Create Date: 2020-12-04 14:01:45.970933

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '633b8140a4d3'
down_revision = '66501d6281ac'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
