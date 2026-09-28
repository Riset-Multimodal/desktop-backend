from typing import List

from fastapi import APIRouter, Depends

from app.api.deps import get_db, get_current_email, require_admin
from app.models.user import User
from sqlalchemy.orm import Session
from app.schemas.user import UserOut

router = APIRouter()

@router.get("/users", response_model=List[UserOut], summary="List all users (khusus admin, butuh X-API-Key)")
def list_users(
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    q = db.query(User).order_by(User.user_email).all()
    return [UserOut.model_validate(r, from_attributes=True) for r in q]


@router.get("/users/me", response_model=UserOut, summary="Profil user yang sedang login")
def me(db: Session = Depends(get_db), email: str = Depends(get_current_email)):
    return UserOut.model_validate(db.get(User, email), from_attributes=True)
