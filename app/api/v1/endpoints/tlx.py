from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.tlx import TlxResponse
from app.schemas.tlx import TlxCreate, TlxOut
from app.services.db_helpers import get_or_create_user

router = APIRouter()

@router.post("/tlx", response_model=TlxOut, summary="Create TLX response")
def create_tlx(payload: TlxCreate, db: Session = Depends(get_db)):
    # pastikan user ada
    get_or_create_user(db, email=str(payload.user_email))

    row = TlxResponse(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return TlxOut.model_validate(row, from_attributes=True)


@router.get("/tlx", response_model=List[TlxOut], summary="List TLX responses (optionally filter by email)")
def list_tlx(
    email: Optional[EmailStr] = Query(None, description="Jika diisi, filter berdasarkan user email"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(TlxResponse).order_by(TlxResponse.created_at.desc())
    if email:
        q = q.filter(TlxResponse.user_email == str(email))
    rows = q.offset(offset).limit(limit).all()
    return [TlxOut.model_validate(r, from_attributes=True) for r in rows]
