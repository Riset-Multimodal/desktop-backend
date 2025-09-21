from datetime import datetime

from pydantic import BaseModel

class UserOut(BaseModel):
    user_email: str
    name: str
    created_at: datetime

    model_config = dict(from_attributes=True)