from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import datetime


class ValidationAnswerEnum(str, Enum):
    FOCUS_TASK = "FOCUS_TASK"
    FOCUS_METHOD = "FOCUS_METHOD"
    THINK_OUTSIDE_TASK = "THINK_OUTSIDE_TASK"


class ValidationCreate(BaseModel):
    user_email: EmailStr
    answer: ValidationAnswerEnum


class ValidationOut(BaseModel):
    id: int
    user_email: EmailStr
    answer: ValidationAnswerEnum
    submitted_at: datetime

    class Config:
        from_attributes = True
