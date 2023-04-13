"""add comments for answer

Revision ID: adb7c669880e
Revises: d7658d797f7b
Create Date: 2023-04-11 23:21:30.974642

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "adb7c669880e"
down_revision = "d7658d797f7b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("answers", sa.Column("comments", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("answers", "comments")
    # ### end Alembic commands ###
