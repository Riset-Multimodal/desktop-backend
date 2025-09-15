from sqlalchemy import (
    String, Integer, Enum, DateTime, ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

from enum import Enum as PyEnum

class ValidationAnswerEnum(PyEnum):
    FOCUS_TASK = "FOCUS_TASK"            # Saya fokus pada tugasnya
    FOCUS_METHOD = "FOCUS_METHOD"        # Saya fokus pada bagaimana saya mengerjakannya
    THINK_OUTSIDE_TASK = "THINK_OUTSIDE_TASK"  # Saya memikirkan hal lain di luar tugas


class ValidationResponse(Base):
    __tablename__ = "validation_responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_email: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("users.user_email", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False
    )
    answer: Mapped[ValidationAnswerEnum] = mapped_column(
        Enum(ValidationAnswerEnum),
        nullable=False
    )
    submitted_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    def __repr__(self):
        return f"<ValidationResponse(id={self.id}, user_email='{self.user_email}', answer='{self.answer.name}')>"
