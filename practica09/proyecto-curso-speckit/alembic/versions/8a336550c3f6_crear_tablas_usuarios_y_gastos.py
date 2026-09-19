"""crear_tablas_usuarios_y_gastos

Revision ID: 8a336550c3f6
Revises: 
Create Date: 2026-09-19 17:09:56.037275

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a336550c3f6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
    )
    op.create_index(op.f("ix_usuarios_email"), "usuarios", ["email"], unique=True)
    op.create_index(op.f("ix_usuarios_id"), "usuarios", ["id"], unique=False)

    op.create_table(
        "gastos",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("descripcion", sa.String(), nullable=False),
        sa.Column("monto", sa.Float(), nullable=False),
        sa.Column("categoria", sa.String(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("fecha", sa.DateTime(), nullable=True),
    )
    op.create_index(op.f("ix_gastos_id"), "gastos", ["id"], unique=False)
    op.create_index(op.f("ix_gastos_categoria"), "gastos", ["categoria"], unique=False)
    op.create_index(op.f("ix_gastos_usuario_id"), "gastos", ["usuario_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_gastos_usuario_id"), table_name="gastos")
    op.drop_index(op.f("ix_gastos_categoria"), table_name="gastos")
    op.drop_index(op.f("ix_gastos_id"), table_name="gastos")
    op.drop_table("gastos")
    op.drop_index(op.f("ix_usuarios_id"), table_name="usuarios")
    op.drop_index(op.f("ix_usuarios_email"), table_name="usuarios")
    op.drop_table("usuarios")
