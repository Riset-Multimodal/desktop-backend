from pydantic import BaseModel

from app.schemas.nordic import NordicCreate, NordicOut
from app.schemas.tlx import TlxCreate, TlxOut
from app.schemas.validation import ValidationCreate, ValidationOut


class QuestionnaireCreate(BaseModel):
    tlx: TlxCreate
    nordic: NordicCreate
    validation: ValidationCreate


class QuestionnaireOut(BaseModel):
    tlx: TlxOut
    nordic: NordicOut
    validation: ValidationOut
