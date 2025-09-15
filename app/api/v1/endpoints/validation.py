from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.validation import ValidationResponse
from app.schemas.validation import ValidationCreate, ValidationOut
from app.services.db_helpers import get_or_create_user

router = APIRouter()

@router.post("/validation", response_model=ValidationOut, summary="Create Validation response")
def create_validation(payload: ValidationCreate, db: Session = Depends(get_db)):
    """
    Membuat jawaban baru untuk survey Validation.
    Jika user belum ada, otomatis dibuat.
    """
    get_or_create_user(db, email=str(payload.user_email))

    row = ValidationResponse(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return ValidationOut.model_validate(row, from_attributes=True)


@router.get("/validation", response_model=List[ValidationOut], summary="List Validation responses (optionally filter by email)")
def list_validation(
    email: Optional[EmailStr] = Query(None, description="Jika diisi, filter berdasarkan user email"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Mengambil daftar jawaban survey Validation.
    Bisa difilter berdasarkan `user_email`.
    """
    q = db.query(ValidationResponse).order_by(ValidationResponse.submitted_at.desc())

    if email:
        q = q.filter(ValidationResponse.user_email == str(email))

    rows = q.offset(offset).limit(limit).all()
    return [ValidationOut.model_validate(r, from_attributes=True) for r in rows]
