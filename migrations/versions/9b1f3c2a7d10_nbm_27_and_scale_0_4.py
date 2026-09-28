"""nordic: add nbm_27 (kaki kanan) and allow scale 0..4

Frontend memakai 0 = "Tidak sakit" dan 1..4 = Ringan..Sangat Berat, tapi
constraint lama hanya menerima 1..4 sehingga jawaban "Tidak sakit" ditolak.

Revision ID: 9b1f3c2a7d10
Revises: 67d588b3e4ad
Create Date: 2026-09-28 06:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b1f3c2a7d10'
down_revision: Union[str, Sequence[str], None] = '67d588b3e4ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE = 'nordic_bodymap_response'


def _drop_nbm_checks() -> None:
    # Constraint lama dibuat tanpa nama, jadi cari namanya dari database.
    for ck in sa.inspect(op.get_bind()).get_check_constraints(TABLE):
        if ck.get('name') and 'nbm_' in (ck.get('sqltext') or ''):
            op.drop_constraint(ck['name'], TABLE, type_='check')


def _create_nbm_checks(low: int, count: int) -> None:
    for i in range(count):
        op.create_check_constraint(f'ck_nbm_{i}', TABLE, f'nbm_{i} BETWEEN {low} AND 4')


def upgrade() -> None:
    """Upgrade schema."""
    # nullable: response lama tidak punya data kaki kanan
    op.add_column(TABLE, sa.Column('nbm_27', sa.SmallInteger(), nullable=True))
    _drop_nbm_checks()
    _create_nbm_checks(0, 28)


def downgrade() -> None:
    """Downgrade schema."""
    _drop_nbm_checks()
    op.drop_column(TABLE, 'nbm_27')
    _create_nbm_checks(1, 27)
