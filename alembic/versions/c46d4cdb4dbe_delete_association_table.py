"""delete association table

Revision ID: c46d4cdb4dbe
Revises: fa5463fff603
Create Date: 2023-03-15 19:44:52.709603

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c46d4cdb4dbe"
down_revision = "fa5463fff603"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("association_table")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "association_table",
        sa.Column("game_id", sa.BIGINT(), autoincrement=False, nullable=True),
        sa.Column("player_id", sa.BIGINT(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["game_id"], ["games.id"], name="association_table_game_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["player_id"],
            ["players.id"],
            name="association_table_player_id_fkey",
        ),
    )
    # ### end Alembic commands ###
