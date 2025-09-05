from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.nordic import NordicBodymapResponse
from app.schemas.nordic import NordicCreate, NordicOut
from app.services.db_helpers import get_or_create_user

router = APIRouter()

@router.post("/nordic", response_model=NordicOut, summary="Create Nordic Body Map response")
def create_nordic(payload: NordicCreate, db: Session = Depends(get_db)):
    # pastikan user ada
    get_or_create_user(db, email=str(payload.user_email))

    row = NordicBodymapResponse(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return NordicOut.model_validate(row, from_attributes=True)


@router.get("/nordic", response_model=List[NordicOut], summary="List Nordic Body Map responses (optionally filter by email)")
def list_nordic(
    email: Optional[EmailStr] = Query(None, description="Jika diisi, filter berdasarkan user email"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(NordicBodymapResponse).order_by(NordicBodymapResponse.created_at.desc())
    if email:
        q = q.filter(NordicBodymapResponse.user_email == str(email))
    rows = q.offset(offset).limit(limit).all()
    return [NordicOut.model_validate(r, from_attributes=True) for r in rows]


@router.get("/nordic/{nbm_id}", response_model=NordicOut, summary="Get 1 Nordic Body Map response by id")
def get_nordic(nbm_id: int, db: Session = Depends(get_db)):
    row = db.get(NordicBodymapResponse, nbm_id)
    if not row:
        raise HTTPException(status_code=404, detail="Nordic response not found")
    return NordicOut.model_validate(row, from_attributes=True)
