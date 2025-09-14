from typing import List

from fastapi import APIRouter, Depends

from app.api.deps import get_db
from app.models.user import User
from sqlalchemy.orm import Session
from app.schemas.user import UserOut

router = APIRouter()

@router.get("/users", response_model=List[UserOut], summary="List All Users that can access the system")
def list_tlx(
    db: Session = Depends(get_db),
):
    q = db.query(User).all()
    return [UserOut.model_validate(r, from_attributes=True) for r in q]