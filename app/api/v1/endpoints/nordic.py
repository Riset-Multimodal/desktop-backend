from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_email, ensure_same_email, get_principal, scope_email, Principal
from app.models.nordic import NordicBodymapResponse
from app.schemas.nordic import NordicCreate, NordicOut
from app.services.db_helpers import get_or_create_user

router = APIRouter()

def build_nordic(db: Session, payload: NordicCreate, email: str) -> NordicBodymapResponse:
    email = ensure_same_email(email, payload.user_email)
    get_or_create_user(db, email=email)
    row = NordicBodymapResponse(**{**payload.model_dump(), "user_email": email})
    db.add(row)
    return row

@router.post("/nordic", response_model=NordicOut, summary="Create Nordic Body Map response")
def create_nordic(payload: NordicCreate, db: Session = Depends(get_db), email: str = Depends(get_current_email)):
    row = build_nordic(db, payload, email)
    db.commit()
    db.refresh(row)
    return NordicOut.model_validate(row, from_attributes=True)


@router.get("/nordic", response_model=List[NordicOut], summary="List Nordic Body Map responses (user: miliknya sendiri, admin: semua)")
def list_nordic(
    email: Optional[EmailStr] = Query(None, description="Jika diisi, filter berdasarkan user email"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_principal),
):
    email = scope_email(principal, email)
    q = db.query(NordicBodymapResponse).order_by(NordicBodymapResponse.created_at.desc())
    if email:
        q = q.filter(NordicBodymapResponse.user_email == str(email))
    rows = q.offset(offset).limit(limit).all()
    return [NordicOut.model_validate(r, from_attributes=True) for r in rows]


@router.get("/nordic/{nbm_id}", response_model=NordicOut, summary="Get 1 Nordic Body Map response by id")
def get_nordic(nbm_id: int, db: Session = Depends(get_db), principal: Principal = Depends(get_principal)):
    row = db.get(NordicBodymapResponse, nbm_id)
    if not row or (not principal.is_admin and row.user_email.lower() != principal.email.lower()):
        raise HTTPException(status_code=404, detail="Nordic response not found")
    return NordicOut.model_validate(row, from_attributes=True)
