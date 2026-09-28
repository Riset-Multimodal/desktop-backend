"""add nbm_27 (kaki kanan) to nordic_bodymap_response

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


def upgrade() -> None:
    """Upgrade schema."""
    # nullable: response lama tidak punya data kaki kanan
    op.add_column('nordic_bodymap_response', sa.Column('nbm_27', sa.SmallInteger(), nullable=True))
    op.create_check_constraint('ck_nbm_27', 'nordic_bodymap_response', 'nbm_27 BETWEEN 1 AND 4')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('ck_nbm_27', 'nordic_bodymap_response', type_='check')
    op.drop_column('nordic_bodymap_response', 'nbm_27')
