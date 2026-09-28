# app/models/nordic_bodymap.py
from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base  # pakai Base kamu


class NordicBodymapResponse(Base):
    """
    1 row = 1 kali pengisian Nordic Body Map.
    Kolom nbm_0..nbm_26 = tingkat keluhan (1..4) sesuai urutan di FE:
      0  leher atas
      1  leher bawah
      2  bahu kiri
      3  bahu kanan
      4  lengan atas kiri
      5  punggung
      6  lengan atas kanan
      7  pinggang
      8  bokong
      9  pantat
      10 siku kiri
      11 siku kanan
      12 lengan bawah kiri
      13 lengan bawah kanan
      14 pergelangan tangan kiri
      15 pergelangan tangan kanan
      16 tangan kiri
      17 tangan kanan
      18 paha kiri
      19 paha kanan
      20 lutut kiri
      21 lutut kanan
      22 betis kiri
      23 betis kanan
      24 pergelangan kaki kiri
      25 pergelangan kaki kanan
      26 kaki kiri
      27 kaki kanan (nullable: response lama sebelum kolom ini ada bernilai NULL)
    """

    __tablename__ = "nordic_bodymap_response"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_email: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.user_email", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # 27 area (skala 1..4)
    nbm_0:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # leher atas
    nbm_1:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # leher bawah
    nbm_2:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # bahu kiri
    nbm_3:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # bahu kanan
    nbm_4:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # lengan atas kiri
    nbm_5:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # punggung
    nbm_6:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # lengan atas kanan
    nbm_7:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # pinggang
    nbm_8:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # bokong
    nbm_9:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # pantat
    nbm_10: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # siku kiri
    nbm_11: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # siku kanan
    nbm_12: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # lengan bawah kiri
    nbm_13: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # lengan bawah kanan
    nbm_14: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # pergelangan tangan kiri
    nbm_15: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # pergelangan tangan kanan
    nbm_16: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # tangan kiri
    nbm_17: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # tangan kanan
    nbm_18: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # paha kiri
    nbm_19: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # paha kanan
    nbm_20: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # lutut kiri
    nbm_21: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # lutut kanan
    nbm_22: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # betis kiri
    nbm_23: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # betis kanan
    nbm_24: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # pergelangan kaki kiri
    nbm_25: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # pergelangan kaki kanan
    nbm_26: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # kaki kiri
    nbm_27: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)  # kaki kanan

    __table_args__ = (
        # validasi skala 1..4 untuk semua kolom
        CheckConstraint("nbm_0  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_1  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_2  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_3  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_4  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_5  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_6  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_7  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_8  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_9  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_10 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_11 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_12 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_13 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_14 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_15 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_16 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_17 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_18 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_19 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_20 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_21 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_22 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_23 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_24 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_25 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_26 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_27 BETWEEN 1 AND 4", name="ck_nbm_27"),
        Index("idx_nbm_response_user_email", "user_email"),
    )

    # helper opsional
    @property
    def total_score(self) -> int:
        return sum(
            getattr(self, f"nbm_{i}") or 0 for i in range(28)
        )
