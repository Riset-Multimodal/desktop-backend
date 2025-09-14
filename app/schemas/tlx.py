from datetime import datetime
from pydantic import BaseModel, EmailStr, conint
from app.models.tlx import TlxFactor  # pakai enum yang sama

# Request body untuk membuat TLX response
class TlxCreate(BaseModel):
    user_email: EmailStr

    # 15 pasangan
    pair_q1:  TlxFactor
    pair_q2:  TlxFactor
    pair_q3:  TlxFactor
    pair_q4:  TlxFactor
    pair_q5:  TlxFactor
    pair_q6:  TlxFactor
    pair_q7:  TlxFactor
    pair_q8:  TlxFactor
    pair_q9:  TlxFactor
    pair_q10: TlxFactor
    pair_q11: TlxFactor
    pair_q12: TlxFactor
    pair_q13: TlxFactor
    pair_q14: TlxFactor
    pair_q15: TlxFactor

    # Likert 1..10
    likert_mental:          conint(ge=1, le=100)
    likert_physical:        conint(ge=1, le=100)
    likert_temporal:        conint(ge=1, le=100)
    likert_performance_raw: conint(ge=1, le=100)
    likert_effort:          conint(ge=1, le=100)
    likert_frustration:     conint(ge=1, le=100)


# Response body
class TlxOut(BaseModel):
    id: int
    user_email: EmailStr
    created_at: datetime

    pair_q1:  TlxFactor
    pair_q2:  TlxFactor
    pair_q3:  TlxFactor
    pair_q4:  TlxFactor
    pair_q5:  TlxFactor
    pair_q6:  TlxFactor
    pair_q7:  TlxFactor
    pair_q8:  TlxFactor
    pair_q9:  TlxFactor
    pair_q10: TlxFactor
    pair_q11: TlxFactor
    pair_q12: TlxFactor
    pair_q13: TlxFactor
    pair_q14: TlxFactor
    pair_q15: TlxFactor

    likert_mental:          int
    likert_physical:        int
    likert_temporal:        int
    likert_performance_raw: int
    likert_effort:          int
    likert_frustration:     int

    # turunan dari model (property)
    likert_performance: int

    model_config = dict(from_attributes=True)
