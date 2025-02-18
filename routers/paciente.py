# Arquivo de rotas para o CRUD de pacientes
from fastapi import HTTPException,status,Depends, APIRouter, Query, Body
from sqlalchemy import column, insert, text, Table, select, delete ,update as sqlalchemy_update, join
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from typing import List
from schemas.database import SessionLocal ,Base, engine, metadata, get_db
from schemas.schema import PutexpCreate, reflect_tables, metadata,Cita,CitaUser,UpdateCitaRequest,Expe,ExpedienteCreate,medico,Paciente_,UsuarioCreate,Paciente
#import logging
#logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
#logger = logging.getLogger(__name__)
router = APIRouter(tags=["Pacientes"])


@router.put("/expediente/{id_paciente}", response_model=Expe)
async def update_exp(
    id_paciente: int,
    expediente_data: PutexpCreate,
    db: Session = Depends(get_db)
):
    tbExp = metadata.tables["expediente"]
    try:
        # Buscar expediente
        result = db.execute(
            select("*")
            .select_from(tbExp)
            .where(tbExp.c.id_paciente == id_paciente)
        ).mappings().first()

        if not result:
            raise HTTPException(status_code=404, detail="Expediente no encontrado")

        # Actualizar
        update_stmt = (
            sqlalchemy_update(tbExp)
            .where(tbExp.c.id_paciente == id_paciente)
            .values(**expediente_data.model_dump())
        )
        
        db.execute(update_stmt)
        db.commit()

        return {**result, **expediente_data.model_dump()}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


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
        stmt = sqlalchemy_update(cita).where(cita.c.id == id).values(data) 
        db.execute(stmt)
        db.commit()

    # Retornar los datos actualizados
    updated_cita = db.query(cita).filter(cita.c.id == id).first()
    return updated_cita


@router.delete("/citas/")
async def Citadelete(paciente_id: int = Query(..., description="ID del paciente"), db: Session = Depends(get_db)):
    # Fetch the cita to delete
    tablaCita = metadata.tables["citas"]

    query = select(tablaCita).where(tablaCita.c.id == paciente_id)
    cita = db.execute(query).fetchone()

    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    try:
        # Delete the cita
        delete_query = delete(tablaCita).where(tablaCita.c.id == paciente_id)
    
        db.execute(delete_query)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar la cita: {str(e)}")
    return {"ok": True}

@router.get("/medicos/",response_model=list[medico])
async def getMedicos(
    skip: int = 0,
    limit: int = 100,
    db : Session = Depends(get_db)):

    medicos = metadata.tables["medico"]
    try:
        result = db.query(medicos).offset(skip).limit(limit).all()
    except: 
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener los médicos")
    finally:
        db.close()
    return result



@router.get("/expediente/", response_model=List[Expe])
async def getExpe(id_paciente: int = Query(..., description="Id del paciente"), db: Session = Depends(get_db)):
    exp = metadata.tables["expediente"]
    query = exp.select().where(exp.columns.id_paciente == id_paciente)
    result = db.execute(query).fetchall()
    if not result:
        raise HTTPException(status_code=404, detail="No se encontraron citas del paciente.")
    try:
        # Versión simplificada y unificada de la consulta
        result = db.execute(
            select("*")
            .select_from(text("expediente"))
            .where(column("id_paciente") == id_paciente)
        ).mappings().all()

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Expediente médico vacío o no encontrado"  # Mensaje más claro
            )
        
        return [Expe(**dict(item)) for item in result]

    except HTTPException as he:
        # Re-lanzamos la excepción HTTP específica
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/citas/")
async def obtenerCita(paciente_id: int = Query(..., description="ID del paciente"), db: Session = Depends(get_db)):
    try:
        tablaCita = metadata.tables["citas"]
        tbMed = metadata.tables["medico"]
        query = select(
                        tablaCita.c.hora,
                        tablaCita.c.fecha,
                        tablaCita.c.motivo,
                        tablaCita.c.id,
                        tablaCita.c.estado,
                        tbMed.c.nombre).select_from(join(
                                tablaCita,
                                tbMed,
                                tablaCita.c.id_medico == tbMed.c.id_medico)).where(tablaCita.columns.id_paciente == paciente_id)
        result = db.execute(query).fetchall()
        # Manejo de resultados vacíos
        if not result:
            raise HTTPException(status_code=404, detail="No se encontraron citas del paciente.")
      # Convertir a una lista de diccionarios
        citas = [dict(row._mapping) for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno : {str(e)}")
    return citas

@router.get("/pacientes/{id}/", response_model= List[Paciente_])
async def users(id:int,db: Session = Depends(get_db))->list[Paciente_]:
    try:
    # Load the "pacientes" table
        pacientes_table = metadata.tables["pacientes"]
        # Create and execute the query
        query = select(pacientes_table).where(pacientes_table.c.id_usuario == id)
        result = db.execute(query).fetchall()
        # Manejo de resultados vacíos
        if not result:
            raise HTTPException(status_code=404, detail="No se encontraron pacientes.")

      # Convertir a una lista de diccionarios
        pacientes = [dict(row._mapping) for row in result]
        return pacientes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno : {str(e)}")

@router.post("/register/paciente/registro2")
def registerPac(paciente: Paciente, db: Session= Depends(get_db)):
    nuevo_paciente = metadata.tables["pacientes"].insert().values(
        fecha_nacimiento=paciente.date,
        sexo=paciente.sexo,
        direccion=paciente.address,
        id_usuario=paciente.id_usuario,
        nombre=paciente.name,
        tel=paciente.tel
    )
    try:
        db.execute(nuevo_paciente)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al registrar el paciente")

    return {"okey": True}

@router.post("/send/citas")
def sendDataCitas(cita: Cita, db: Session= Depends(get_db)):
    citaTabla = metadata.tables["citas"] 
    query = select(citaTabla).where((citaTabla.c.fecha == cita.fecha) & (citaTabla.c.hora == cita.hora)& (citaTabla.c.id_medico == cita.id_medico))
    check = db.execute(query).fetchone()    
    if check: raise HTTPException(status_code=400,detail=" Ya esta Registrado esa Fecha y Hora")
    newCita = metadata.tables["citas"].insert().values(
        id_paciente = cita.id_paciente,
        fecha = cita.fecha,
        hora = cita.hora,
        motivo = cita.motivo,
        id_medico = cita.id_medico
    )
    try:
        db.execute(newCita)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500,detail=f"Error al Registrar la Cita : {str(e)}")
    return {"okey": True}

@router.post("/expediente/", response_model=ExpedienteCreate)
async def create_exp(
    expediente_data: ExpedienteCreate,
    db: Session = Depends(get_db)
):
    try:
        # Convertir usando alias
        db_data = expediente_data.model_dump()
        
        stmt = insert(metadata.tables["expediente"]).values(**db_data).returning("*")
        result = (db.execute(stmt)).mappings().first()
        db.commit()
        
        return result

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno: {str(e)}"
        )