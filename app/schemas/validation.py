from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import datetime
from typing import Optional


class ValidationAnswerEnum(str, Enum):
    FOCUS_TASK = "FOCUS_TASK"
    FOCUS_METHOD = "FOCUS_METHOD"
    THINK_OUTSIDE_TASK = "THINK_OUTSIDE_TASK"


class ValidationCreate(BaseModel):
    # opsional: email diambil dari token login; kalau diisi harus sama
    user_email: Optional[EmailStr] = None
    answer: ValidationAnswerEnum


class ValidationOut(BaseModel):
    id: int
    user_email: EmailStr
    answer: ValidationAnswerEnum
    submitted_at: datetime

    model_config = dict(from_attributes=True)
