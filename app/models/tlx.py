# app/models/tlx.py
from __future__ import annotations
import enum
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger, String, func, Index
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class TlxFactor(enum.Enum):
    mental = "mental"
    physical = "physical"
    temporal = "temporal"
    performance = "performance"
    effort = "effort"
    frustration = "frustration"

# biar Alembic yang mengelola create/drop type
TlxFactorEnum = PGEnum(TlxFactor, name="tlx_factor", create_type=False)

class TlxResponse(Base):
    __tablename__ = "tlx_response"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_email: Mapped[str] = mapped_column(
        String,                                           # ← tipe DULU
        ForeignKey("users.user_email", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # pasangan
    pair_q1:  Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q2:  Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q3:  Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q4:  Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q5:  Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q6:  Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q7:  Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q8:  Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q9:  Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q10: Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q11: Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q12: Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q13: Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q14: Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q15: Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)

    # likert 1..100 (ingat: SmallInteger + constraint)
    likert_mental:          Mapped[int] = mapped_column(SmallInteger, nullable=False)
    likert_physical:        Mapped[int] = mapped_column(SmallInteger, nullable=False)
    likert_temporal:        Mapped[int] = mapped_column(SmallInteger, nullable=False)
    likert_performance_raw: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    likert_effort:          Mapped[int] = mapped_column(SmallInteger, nullable=False)
    likert_frustration:     Mapped[int] = mapped_column(SmallInteger, nullable=False)

    __table_args__ = (
        CheckConstraint("likert_mental BETWEEN 1 AND 100", name="ck_likert_mental"),
        CheckConstraint("likert_physical BETWEEN 1 AND 100", name="ck_likert_physical"),
        CheckConstraint("likert_temporal BETWEEN 1 AND 100", name="ck_likert_temporal"),
        CheckConstraint("likert_performance_raw BETWEEN 1 AND 100", name="ck_likert_performance_raw"),
        CheckConstraint("likert_effort BETWEEN 1 AND 100", name="ck_likert_effort"),
        CheckConstraint("likert_frustration BETWEEN 1 AND 100", name="ck_likert_frustration"),
        # kalau sudah pakai index=True di kolom, HAPUS index manual ini agar tidak dobel
        # Index("idx_tlx_response_user_email", "user_email"),
    )

    @property
    def likert_performance(self) -> int:
        # skala dibalik: 1..100 -> 100..1
        return 101 - int(self.likert_performance_raw)
