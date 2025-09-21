from sqlalchemy import String, Integer, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Keylog(Base):
    __tablename__ = "keylog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_email: Mapped[str] = mapped_column(String, index=True)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    type: Mapped[str | None] = mapped_column(String)

    keystroke_count: Mapped[int | None] = mapped_column(Integer)
    left_click_count: Mapped[int | None] = mapped_column(Integer)
    right_click_count: Mapped[int | None] = mapped_column(Integer)
    scroll_up: Mapped[int | None] = mapped_column(Integer)
    scroll_down: Mapped[int | None] = mapped_column(Integer)
    space_count: Mapped[int | None] = mapped_column(Integer)

    error_rate: Mapped[float | None] = mapped_column(Float)
    mean_dwell_time_ms: Mapped[float | None] = mapped_column(Float)
    std_dev_dwell_time_ms: Mapped[float | None] = mapped_column(Float)
    mean_flight_time_ms: Mapped[float | None] = mapped_column(Float)
    std_dev_flight_time_ms: Mapped[float | None] = mapped_column(Float)
    mean_digraph_time_ms: Mapped[float | None] = mapped_column(Float)
    std_dev_digraph_time_ms: Mapped[float | None] = mapped_column(Float)
    pause_count: Mapped[int | None] = mapped_column(Integer)
    mean_pause_duration_ms: Mapped[float | None] = mapped_column(Float)
    mean_burst_length: Mapped[float | None] = mapped_column(Float)

    words_per_minute: Mapped[float | None] = mapped_column(Float)
    typing_rhythm_consistency: Mapped[float | None] = mapped_column(Float)
    mouse_speed: Mapped[float | None] = mapped_column(Float)
    mouse_accuracy: Mapped[float | None] = mapped_column(Float)
    mouse_jerkiness: Mapped[float | None] = mapped_column(Float)
    raw_x_sequence: Mapped[str | None] = mapped_column(String)
    raw_y_sequence: Mapped[str | None] = mapped_column(String)

