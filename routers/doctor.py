from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.database import get_db
from schemas.schema import * 

# Router específico para doctores SIN prefijo aquí
router = APIRouter(tags=["Doctores"])  # Tags para documentación Swagger

@router.get("/doctor/{id_doctor}", response_model=list[Cita])
async def getCitas(id_doctor : int, db: Session = Depends(get_db)) -> list[Cita]:
    tbCitas = metadata.tables["citas"]
    query = tbCitas.select().where(tbCitas.c.id_medico == id_doctor)
    r= db.execute(query).fetchall()
    print(r)
    return dict(r)
