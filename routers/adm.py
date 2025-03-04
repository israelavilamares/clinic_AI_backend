from fastapi import APIRouter, Depends,HTTPException, status
from schemas.database import get_db, metadata
from schemas.schema import meDoctor
from sqlalchemy import  or_
from sqlalchemy.orm import Session

router = APIRouter(tags=["administradores"])

false = 0
@router.get('/',response_model=list[meDoctor])
def medicos(skip:int=0,limit=100,db: Session = Depends(get_db)):#add verificacion si es true todavia existe
    doc = metadata.tables["medico"]
    try:query = db.query(doc).filter(or_(
        doc.c.is_delete == False,
        doc.c.is_delete.is_(None)
    )).offset(skip).limit(limit).all()
    except:raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al obtener los médicos")
    finally:db.close()
    return query

@router.put('/')
def editMedico(id:int,db: Session = Depends(get_db)):
    doc = metadata.tables["medico"]
    try:db.query(doc).filter(doc.c.id==id).update({"nombre":"Juan"})
    except:raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al editar el médico")
    finally:db.commit()
    return {"mensaje":"Médico editado correctamente"}

@router.post('/')
def add():
    


    return {"mensaje":"Médico agregado correctamente"}