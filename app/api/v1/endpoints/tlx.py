from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_email, ensure_same_email, get_principal, scope_email, Principal
from app.models.tlx import TlxResponse
from app.schemas.tlx import TlxCreate, TlxOut
from app.services.db_helpers import get_or_create_user

router = APIRouter()

def build_tlx(db: Session, payload: TlxCreate, email: str) -> TlxResponse:
    email = ensure_same_email(email, payload.user_email)
    get_or_create_user(db, email=email)
    row = TlxResponse(**{**payload.model_dump(), "user_email": email})
    db.add(row)
    return row

@router.post("/tlx", response_model=TlxOut, summary="Create TLX response")
def create_tlx(payload: TlxCreate, db: Session = Depends(get_db), email: str = Depends(get_current_email)):
    row = build_tlx(db, payload, email)
    db.commit()
    db.refresh(row)
    return TlxOut.model_validate(row, from_attributes=True)


@router.get("/tlx", response_model=List[TlxOut], summary="List TLX responses (user: miliknya sendiri, admin: semua)")
def list_tlx(
    email: Optional[EmailStr] = Query(None, description="Jika diisi, filter berdasarkan user email"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_principal),
):
    email = scope_email(principal, email)
    q = db.query(TlxResponse).order_by(TlxResponse.created_at.desc())
    if email:
        q = q.filter(TlxResponse.user_email == str(email))
    rows = q.offset(offset).limit(limit).all()
    return [TlxOut.model_validate(r, from_attributes=True) for r in rows]
