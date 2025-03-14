from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.sql import select,update
from sqlalchemy.orm import Session
from schemas.database import get_db, metadata
from schemas.schema import * 

# Router específico para doctores SIN prefijo aquí
router = APIRouter(tags=["Doctores"])  # Tags para documentación Swagger


@router.put("/citas/", response_model=CitaUser)
async def updateCita( id: int = Query(..., description="ID citas"), request: UpdateCitaRequest = Body(...),db: Session = Depends(get_db)):
    cita = metadata.tables["citas"]
    print(id)

    # Verificar si la cita existe
    existing_cita = db.query(cita).filter(cita.c.id == id).first()
    if not existing_cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    data = {}
    if request.motivo and request.motivo.strip():  
        data["motivo"] = request.motivo
    if request.estado and request.estado.strip():  
        data["estado"] = request.estado
    

    if data:
        # Ejecutar la actualización en la base de datos
        stmt = update(cita).where(cita.c.id == id).values(data) 
        db.execute(stmt)
        db.commit()

    # Retornar los datos actualizados
    updated_cita = db.query(cita).filter(cita.c.id == id).first()
    return updated_cita


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

@router.get("/yo/{id}",response_model=meDoctor) # aqui solo necesitamos un solo objeto y no una lista de objetos
async def getMe(id:int, db: Session = Depends(get_db)):
    
    tbMed = metadata.tables["medico"]
    query = select(tbMed).where(tbMed.c.id_usuario == id)
    r = db.execute(query).mappings().fetchone()
    if r == None: raise HTTPException(status_code=404, detail="No se encontraron doctores.")
    return r


