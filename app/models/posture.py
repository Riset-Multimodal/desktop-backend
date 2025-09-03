from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime, UniqueConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Posture(Base):
    __tablename__ = "posture"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_email: Mapped[str] = mapped_column(String, index=True)
    capture_id: Mapped[str] = mapped_column(String, index=True)
    timestamp: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())

    front_image_link: Mapped[str | None] = mapped_column(String)
    side_image_link: Mapped[str | None] = mapped_column(String)
    overhead_image_link: Mapped[str | None] = mapped_column(String)

    # Chair state
    chair_state_armrest_adjustable: Mapped[bool | None] = mapped_column(Boolean)
    chair_state_armrest_height_from_seat: Mapped[float | None] = mapped_column(Float)
    chair_state_armrest_surface_hard: Mapped[bool | None] = mapped_column(Boolean)
    chair_state_armrests_too_wide: Mapped[bool | None] = mapped_column(Boolean)
    chair_state_back_contact_percentage: Mapped[float | None] = mapped_column(Float)
    chair_state_backrest_adjustable: Mapped[bool | None] = mapped_column(Boolean)
    chair_state_elbow_angle: Mapped[float | None] = mapped_column(Float)
    chair_state_feet_on_floor: Mapped[bool | None] = mapped_column(Boolean)
    chair_state_foot_contact_percentage: Mapped[float | None] = mapped_column(Float)
    chair_state_forearm_support_contact: Mapped[bool | None] = mapped_column(Boolean)
    chair_state_gap_behind_knee: Mapped[float | None] = mapped_column(Float)
    chair_state_height_adjustable: Mapped[bool | None] = mapped_column(Boolean)
    chair_state_knee_angle: Mapped[float | None] = mapped_column(Float)
    chair_state_knee_clearance: Mapped[float | None] = mapped_column(Float)
    chair_state_leg_room_width: Mapped[float | None] = mapped_column(Float)
    chair_state_lumbar_contact: Mapped[bool | None] = mapped_column(Boolean)
    chair_state_lumbar_curve_match: Mapped[float | None] = mapped_column(Float)
    chair_state_pan_depth_adjustable: Mapped[bool | None] = mapped_column(Boolean)
    chair_state_recline_angle: Mapped[float | None] = mapped_column(Float)
    chair_state_shoulder_elevation: Mapped[bool | None] = mapped_column(Boolean)
    chair_state_thigh_pressure: Mapped[bool | None] = mapped_column(Boolean)
    chair_state_thigh_support_length: Mapped[float | None] = mapped_column(Float)
    chair_state_work_surface_too_high: Mapped[bool | None] = mapped_column(Boolean)

    # Final scores
    final_scores_bc_combined_score: Mapped[int | None] = mapped_column(Integer)
    final_scores_final_rosa_score: Mapped[int | None] = mapped_column(Integer)
    final_scores_section_a_score: Mapped[int | None] = mapped_column(Integer)
    final_scores_section_b_score: Mapped[int | None] = mapped_column(Integer)
    final_scores_section_c_score: Mapped[int | None] = mapped_column(Integer)

    # Monitor / Phone state
    monitor_phone_state_has_glare: Mapped[bool | None] = mapped_column(Boolean)
    monitor_phone_state_has_neck_twist: Mapped[bool | None] = mapped_column(Boolean)
    monitor_phone_state_monitor_consecutive_minutes: Mapped[int | None] = mapped_column(Integer)
    monitor_phone_state_monitor_too_far: Mapped[bool | None] = mapped_column(Boolean)
    monitor_phone_state_monitor_too_high: Mapped[bool | None] = mapped_column(Boolean)
    monitor_phone_state_monitor_too_low: Mapped[bool | None] = mapped_column(Boolean)
    monitor_phone_state_no_doc_holder: Mapped[bool | None] = mapped_column(Boolean)
    monitor_phone_state_no_hands_free: Mapped[bool | None] = mapped_column(Boolean)
    monitor_phone_state_phone_consecutive_minutes: Mapped[int | None] = mapped_column(Integer)
    monitor_phone_state_phone_too_far: Mapped[bool | None] = mapped_column(Boolean)
    monitor_phone_state_use_neck_shoulder_hold: Mapped[bool | None] = mapped_column(Boolean)

    # Mouse / Keyboard state
    mouse_keyboard_state_deviation_while_typing: Mapped[bool | None] = mapped_column(Boolean)
    mouse_keyboard_state_keyboard_consecutive_minutes: Mapped[int | None] = mapped_column(Integer)
    mouse_keyboard_state_keyboard_duration_hours: Mapped[int | None] = mapped_column(Integer)
    mouse_keyboard_state_keyboard_platform_non_adjustable: Mapped[bool | None] = mapped_column(Boolean)
    mouse_keyboard_state_keyboard_too_high: Mapped[bool | None] = mapped_column(Boolean)
    mouse_keyboard_state_mouse_consecutive_minutes: Mapped[int | None] = mapped_column(Integer)
    mouse_keyboard_state_mouse_duration_hours: Mapped[int | None] = mapped_column(Integer)
    mouse_keyboard_state_mouse_keyboard_on_different_surfaces: Mapped[bool | None] = mapped_column(Boolean)
    mouse_keyboard_state_palmrest_in_front_of_mouse: Mapped[bool | None] = mapped_column(Boolean)
    mouse_keyboard_state_pinch_grip_on_mouse: Mapped[bool | None] = mapped_column(Boolean)
    mouse_keyboard_state_reaching_to_mouse: Mapped[bool | None] = mapped_column(Boolean)
    mouse_keyboard_state_reaching_to_overhead_items: Mapped[bool | None] = mapped_column(Boolean)
    mouse_keyboard_state_wrists_extended: Mapped[bool | None] = mapped_column(Boolean)

    # Score A results
    score_a_results_armrest_score: Mapped[int | None] = mapped_column(Integer)
    score_a_results_arms_back_axis: Mapped[int | None] = mapped_column(Integer)
    score_a_results_backrest_score: Mapped[int | None] = mapped_column(Integer)
    score_a_results_chair_base_score: Mapped[int | None] = mapped_column(Integer)
    score_a_results_depth_score: Mapped[int | None] = mapped_column(Integer)
    score_a_results_final_score: Mapped[int | None] = mapped_column(Integer)
    score_a_results_height_score: Mapped[int | None] = mapped_column(Integer)
    score_a_results_seat_pan_axis: Mapped[int | None] = mapped_column(Integer)

    # Score B results
    score_b_results_final_b_score: Mapped[int | None] = mapped_column(Integer)
    score_b_results_monitor_score: Mapped[int | None] = mapped_column(Integer)
    score_b_results_phone_score: Mapped[int | None] = mapped_column(Integer)

    # Score C results
    score_c_results_final_c_score: Mapped[int | None] = mapped_column(Integer)
    score_c_results_keyboard_score: Mapped[int | None] = mapped_column(Integer)
    score_c_results_mouse_score: Mapped[int | None] = mapped_column(Integer)

    __table_args__ = (
        UniqueConstraint("user_email", "capture_id", name="uq_posture_user_capture"),
    )
