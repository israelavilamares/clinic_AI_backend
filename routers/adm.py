from fastapi import APIRouter, Depends,HTTPException, status
from schemas.database import get_db, metadata
from schemas.schema import meDoctor
#from sqlalchemy.sql import select
from sqlalchemy.orm import Session

router = APIRouter(tags=["administradores"])

@router.get('/',response_model=list[meDoctor])
def medicos(skip:int=0,limit=100,db: Session = Depends(get_db)):
    doc = metadata.tables["medico"]
    try:query = db.query(doc).offset(skip).limit(limit).all()
    except:raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al obtener los médicos")
    finally:db.close()
    return query
