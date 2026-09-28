from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class UserOut(BaseModel):
    user_email: str
    # nullable di DB (user yang dibuat otomatis belum punya nama/fakultas)
    name: Optional[str] = None
    faculty: Optional[str] = None
    created_at: datetime

    model_config = dict(from_attributes=True)
