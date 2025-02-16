import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import Form, Query, Body, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException,status,Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Annotated
from sqlalchemy import column, insert, text, Table, select, delete ,update as sqlalchemy_update, join
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
import uvicorn
import doctor
from passwords import hash_passwords, verify_password # retorna verify un resultado booleano 
from schemas.database import SessionLocal ,Base, engine, metadata, get_db
from schemas.schema import PutexpCreate, reflect_tables, metadata,Cita,CitaUser,UpdateCitaRequest,Expe,ExpedienteCreate,medico,Paciente_,UsuarioCreate,Paciente
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import logging

#logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
#logger = logging.getLogger(__name__)

app= FastAPI()

origins = [
   
    "http://localhost:3000",  # Dirección del cliente React
      # Dirección donde se ejecuta React en desarrollo
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los encabezados
)


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 50

api_v1_router = APIRouter(prefix="/api/v1")

# Incluir el router de doctores bajo el prefijo /api/v1
api_v1_router.include_router(doctor.router)

# Registrar el router principal en la app
app.include_router(api_v1_router)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


#es lo que tiene que devolver
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol:str
    id: int


class OAuth2PasswordRequestFormEmail(OAuth2PasswordRequestForm):
    def __init__(self, email: str = Form(...), password: str = Form(...)):
        super().__init__(username=email, password=password)

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestFormEmail = Depends(), db: Session = Depends(get_db)):
    # Buscar usuario por email
    #paciente = db.query()

    user = db.query(metadata.tables["usuario"]).filter_by(email=form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Crear token de acceso
    access_token = create_access_token(data={"sub": user.email})


    # Obtener el rol del usuario
    rol = user.rol
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="error rol"
        )     
    return {"access_token": access_token, "token_type": "bearer", "rol": rol,"id":user.id}


@app.put("/expediente/{id_paciente}", response_model=Expe)
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


@app.put("/citas/", response_model=CitaUser)
async def updateCita(
    id: int = Query(..., description="ID citas"), 
    request: UpdateCitaRequest = Body(...),
    db: Session = Depends(get_db)
):
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


@app.delete("/citas/")
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


@app.get("/medicos/",response_model=list[medico])# add here schema
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



@app.get("/expediente/", response_model=List[Expe])
async def getExpe(
    id_paciente: int = Query(..., description="Id del paciente"),
    db: Session = Depends(get_db)
):
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

@app.get("/citas/")
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
                                tablaCita.c.id_medico == tbMed.c.id_medico)).where(
                                    tablaCita.columns.id_paciente == paciente_id)
        

        result = db.execute(query).fetchall()
       
        # Manejo de resultados vacíos
        if not result:
            raise HTTPException(status_code=404, detail="No se encontraron citas del paciente.")

        # Transformar las filas en objetos Pydantic
         # Transformar los resultados en una lista compatible con Pydantic
      # Convertir a una lista de diccionarios
        citas = [dict(row._mapping) for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno : {str(e)}")

    return citas



@app.get("/pacientes/{id}/", response_model= List[Paciente_])
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

        # Transformar las filas en objetos Pydantic
         # Transformar los resultados en una lista compatible con Pydantic
      # Convertir a una lista de diccionarios
        pacientes = [dict(row._mapping) for row in result]

        return pacientes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno : {str(e)}")



# Endpoint para registrar un usuario
@app.post("/register")
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):

    usuario_existente = db.query(metadata.tables["usuario"]).filter_by(email=usuario.email).first()
    if usuario_existente:
       raise HTTPException(status_code=400, detail="El email ya existe")
    # Insertar el nuevo usuario
    hashed_password = hash_passwords(usuario.password)
    nuevo_usuario = metadata.tables["usuario"].insert().values(
        username=usuario.username, 
        email=usuario.email,
        password=hashed_password,
    )
    try:
        result = db.execute(nuevo_usuario)
        db.commit()
        user_id = result.inserted_primary_key[0]
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al registrar el usuario")
    return {"mensaje": "Usuario registrado exitosamente","user_id": user_id}



@app.post("/register/paciente/registro2")
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


@app.post("/send/citas")
def sendDataCitas(cita: Cita, db: Session= Depends(get_db)):

    citaTabla = metadata.tables["citas"] 

    query = select(citaTabla).where((citaTabla.c.fecha == cita.fecha) & (citaTabla.c.hora == cita.hora)& (citaTabla.c.id_medico == cita.id_medico))
    check = db.execute(query).fetchone()
    
    if check:
        raise HTTPException(status_code=400,detail=" Ya esta Registrado esa Fecha y Hora")


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

    return {"mensaje": "Paciente registrado exitosamente"}


@app.post("/expediente/", response_model=ExpedienteCreate)
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



if __name__=="__main__":
    uvicorn.run("main:app",port=8000,reload=True)