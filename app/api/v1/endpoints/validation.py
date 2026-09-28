from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_email, ensure_same_email, get_principal, scope_email, Principal
from app.models.validation import ValidationResponse
from app.schemas.validation import ValidationCreate, ValidationOut
from app.services.db_helpers import get_or_create_user

router = APIRouter()

def build_validation(db: Session, payload: ValidationCreate, email: str) -> ValidationResponse:
    email = ensure_same_email(email, payload.user_email)
    get_or_create_user(db, email=email)
    row = ValidationResponse(**{**payload.model_dump(), "user_email": email})
    db.add(row)
    return row

@router.post("/validation", response_model=ValidationOut, summary="Create Validation response")
def create_validation(payload: ValidationCreate, db: Session = Depends(get_db), email: str = Depends(get_current_email)):
    """
    Membuat jawaban baru untuk survey Validation milik user yang login.
    """
    row = build_validation(db, payload, email)
    db.commit()
    db.refresh(row)
    return ValidationOut.model_validate(row, from_attributes=True)


@router.get("/validation", response_model=List[ValidationOut], summary="List Validation responses (user: miliknya sendiri, admin: semua)")
def list_validation(
    email: Optional[EmailStr] = Query(None, description="Jika diisi, filter berdasarkan user email"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_principal),
):
    """
    Mengambil daftar jawaban survey Validation.
    User biasa hanya melihat miliknya sendiri; admin (X-API-Key) bisa filter bebas.
    """
    email = scope_email(principal, email)
    q = db.query(ValidationResponse).order_by(ValidationResponse.submitted_at.desc())

    if email:
        q = q.filter(ValidationResponse.user_email == str(email))

    rows = q.offset(offset).limit(limit).all()
    return [ValidationOut.model_validate(r, from_attributes=True) for r in rows]
