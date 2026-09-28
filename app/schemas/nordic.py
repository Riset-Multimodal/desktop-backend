from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, conint

# Request body (buat 1 submission)
class NordicCreate(BaseModel):
    # opsional: email diambil dari token login; kalau diisi harus sama
    user_email: Optional[EmailStr] = None

    # 27 area skala 1..4
    nbm_0:  conint(ge=1, le=4)
    nbm_1:  conint(ge=1, le=4)
    nbm_2:  conint(ge=1, le=4)
    nbm_3:  conint(ge=1, le=4)
    nbm_4:  conint(ge=1, le=4)
    nbm_5:  conint(ge=1, le=4)
    nbm_6:  conint(ge=1, le=4)
    nbm_7:  conint(ge=1, le=4)
    nbm_8:  conint(ge=1, le=4)
    nbm_9:  conint(ge=1, le=4)
    nbm_10: conint(ge=1, le=4)
    nbm_11: conint(ge=1, le=4)
    nbm_12: conint(ge=1, le=4)
    nbm_13: conint(ge=1, le=4)
    nbm_14: conint(ge=1, le=4)
    nbm_15: conint(ge=1, le=4)
    nbm_16: conint(ge=1, le=4)
    nbm_17: conint(ge=1, le=4)
    nbm_18: conint(ge=1, le=4)
    nbm_19: conint(ge=1, le=4)
    nbm_20: conint(ge=1, le=4)
    nbm_21: conint(ge=1, le=4)
    nbm_22: conint(ge=1, le=4)
    nbm_23: conint(ge=1, le=4)
    nbm_24: conint(ge=1, le=4)
    nbm_25: conint(ge=1, le=4)
    nbm_26: conint(ge=1, le=4)
    nbm_27: Optional[conint(ge=1, le=4)] = None  # kaki kanan

# Response body
class NordicOut(BaseModel):
    id: int
    user_email: EmailStr
    created_at: datetime

    nbm_0:  int; nbm_1:  int; nbm_2:  int; nbm_3:  int; nbm_4:  int; nbm_5:  int; nbm_6:  int
    nbm_7:  int; nbm_8:  int; nbm_9:  int; nbm_10: int; nbm_11: int; nbm_12: int; nbm_13: int
    nbm_14: int; nbm_15: int; nbm_16: int; nbm_17: int; nbm_18: int; nbm_19: int; nbm_20: int
    nbm_21: int; nbm_22: int; nbm_23: int; nbm_24: int; nbm_25: int; nbm_26: int
    nbm_27: Optional[int] = None

    # property helper dari model
    total_score: int

    model_config = dict(from_attributes=True)
