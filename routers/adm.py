from fastapi import APIRouter, Depends,HTTPException, status
from schemas.database import get_db, metadata
from schemas.schema import meDoctor
from sqlalchemy import  or_, insert
from sqlalchemy.orm import Session

router = APIRouter(tags=["administradores"])

@router.get('/doctor',response_model=list[meDoctor])# here to need to return everyone doctors exist
def getMedicos(skip:int=0,limit=100,db: Session = Depends(get_db)):#add verificacion si es true todavia existe
    doc = metadata.tables["medico"]
    try:query = db.query(doc).filter(or_(
        doc.c.is_delete == False,
        doc.c.is_delete.is_(None)
    )).offset(skip).limit(limit).all()
    except:raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al obtener los médicos")
    if not query:raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay médicos registrados")
    return query

@router.put('/')
def editMedico(id:int,db: Session = Depends(get_db)):
    doc = metadata.tables["medico"]
    try:db.query(doc).filter(doc.c.id==id).update({"nombre":"Juan"})
    except:raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al editar el médico")
    finally:db.commit()
    return {"mensaje":"Médico editado correctamente"}

@router.post('/doctor',response_model=meDoctor)
#Newdoctor es el objeto que tiene los datos para mandar
def Postmedico(Newdoctor:meDoctor,db: Session = Depends(get_db)):
    try: 
        data = Newdoctor.model_dump()
        stmt = insert(metadata.tables["medico"]).values(**data).returning("*")
        result = db.execute(stmt).mappings().first()
        db.commit()
        return result
    except:
        #eliminar solo cambia el estatus
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error at add doctor")

#----------------------------------------------------------------#
#
#necesito una funcion para agregar un usuario primero antes que un doctor
#
#----------------------------------------------------------------#
