from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.sql import select
from sqlalchemy.orm import Session
from schemas.database import get_db, metadata
from schemas.schema import * 

# Router específico para doctores SIN prefijo aquí
router = APIRouter(tags=["Doctores"])  # Tags para documentación Swagger

@router.get("/citas/{id}", response_model=list[CitaD])
async def getCitas(id : int, db: Session = Depends(get_db)):
    tbMed = metadata.tables["medico"]
    doctor = select(tbMed.c.id_medico).where(tbMed.c.id_usuario == id)
    runDoc = db.execute(doctor).fetchone()
    id_d = runDoc[0]
    tbCitas = metadata.tables["citas"]
    query = tbCitas.select().where(tbCitas.c.id_medico == id_d)
    r= db.execute(query).mappings().fetchall()
    if r == []: raise HTTPException(status_code=404, detail="No se encontraron doctores.")
    return r

@router.get("/me/{id}",response_model=meDoctor) # aqui solo necesitamos un solo objeto y no una lista de objetos
async def getMe(id:int, db: Session = Depends(get_db)):
    
    tbMed = metadata.tables["medico"]
    query = select(tbMed).where(tbMed.c.id_usuario == id)
    r = db.execute(query).mappings().fetchone()
    if r == None: raise HTTPException(status_code=404, detail="No se encontraron doctores.")
    return r


