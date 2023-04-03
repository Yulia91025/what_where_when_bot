"""add admin, question and answer models

Revision ID: 04d67f933d19
Revises: 319cc7e7fe50
Create Date: 2023-03-27 17:35:16.867114

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "04d67f933d19"
down_revision = "b86f26160e3b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("answers")
    op.drop_table("admins")
    op.drop_table("questions")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "questions",
        sa.Column(
            "id",
            sa.BIGINT(),
            sa.Identity(
                always=False,
                start=1,
                increment=1,
                minvalue=1,
                maxvalue=9223372036854775807,
                cycle=False,
                cache=1,
            ),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("title", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="questions_pkey"),
        sa.UniqueConstraint("title", name="questions_title_key"),
        postgresql_ignore_search_path=False,
    )
    op.create_table(
        "admins",
        sa.Column(
            "id",
            sa.BIGINT(),
            sa.Identity(
                always=False,
                start=1,
                increment=1,
                minvalue=1,
                maxvalue=9223372036854775807,
                cycle=False,
                cache=1,
            ),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("email", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("password", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="admins_pkey"),
        sa.UniqueConstraint("email", name="admins_email_key"),
    )
    op.create_table(
        "answers",
        sa.Column(
            "id",
            sa.BIGINT(),
            sa.Identity(
                always=False,
                start=1,
                increment=1,
                minvalue=1,
                maxvalue=9223372036854775807,
                cycle=False,
                cache=1,
            ),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("title", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "is_correct", sa.BOOLEAN(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "question_id", sa.BIGINT(), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["questions.id"],
            name="answers_question_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="answers_pkey"),
    )
    # ### end Alembic commands ###
