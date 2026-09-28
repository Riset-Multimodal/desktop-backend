from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_email
from app.api.v1.endpoints.nordic import build_nordic
from app.api.v1.endpoints.tlx import build_tlx
from app.api.v1.endpoints.validation import build_validation
from app.schemas.nordic import NordicOut
from app.schemas.questionnaire import QuestionnaireCreate, QuestionnaireOut
from app.schemas.tlx import TlxOut
from app.schemas.validation import ValidationOut

router = APIRouter()


@router.post("/questionnaire", response_model=QuestionnaireOut, summary="Simpan TLX + Nordic + Validation dalam satu transaksi")
def create_questionnaire(
    payload: QuestionnaireCreate,
    db: Session = Depends(get_db),
    email: str = Depends(get_current_email),
):
    # Semua tersimpan atau tidak sama sekali, jadi retry dari client tidak membuat data dobel.
    tlx = build_tlx(db, payload.tlx, email)
    nordic = build_nordic(db, payload.nordic, email)
    validation = build_validation(db, payload.validation, email)
    db.commit()
    for row in (tlx, nordic, validation):
        db.refresh(row)
    return QuestionnaireOut(
        tlx=TlxOut.model_validate(tlx, from_attributes=True),
        nordic=NordicOut.model_validate(nordic, from_attributes=True),
        validation=ValidationOut.model_validate(validation, from_attributes=True),
    )
