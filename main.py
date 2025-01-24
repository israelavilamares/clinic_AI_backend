from fastapi import FastAPI
from fastapi import Form, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException,status,Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Annotated
from sqlalchemy import text, Table, select, delete ,update as sqlalchemy_update
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
import uvicorn
from passwords import  hash_passwords, verify_password # retorna verify un resultado booleano 
from database import SessionLocal ,Base, engine, metadata, get_db
from models import reflect_tables, metadata,Cita,CitaUser,UpdateCitaRequest
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

#SECRET_KEY = os.getenv()
# Clave secreta para firmar el token
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 50


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
    print(data)

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
    return {"mensaje": "Cita eliminada correctamente"}


@app.get("/citas/")
async def obtenerCita(paciente_id: int = Query(..., description="ID del paciente"), db: Session = Depends(get_db)):
    
    try:
        tablaCita = metadata.tables["citas"]

       
        query = tablaCita.select().where(tablaCita.columns.id_paciente == paciente_id)
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


class Paciente_(BaseModel):  
    id_paciente: int
#    fecha_naciemiento: datetime
    sexo: str
    direccion: str
    is_delete: bool
    nombre: str
    tel: int

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


class UsuarioCreate(BaseModel):
    username:str
    email: str
    password: str

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


class Paciente(BaseModel):
    date: str
    sexo: str
    id_usuario : int  
    address : str
    name: str
    tel: str


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

    return {"mensaje": "Paciente registrado exitosamente"}


@app.post("/send/citas")
def sendDataCitas(cita: Cita, db: Session= Depends(get_db)):

    citaTabla = metadata.tables["citas"]; 

    query = select(citaTabla).where((citaTabla.c.fecha == cita.fecha) & (citaTabla.c.hora == cita.hora))
    check = db.execute(query).fetchone()
    
    if check:
        raise HTTPException(status_code=400,detail=" Ya esta Registrado esa Fecha y Hora")


    newCita = metadata.tables["citas"].insert().values(
        id_paciente = cita.id_paciente,
        fecha = cita.fecha,
        hora = cita.hora,
        motivo = cita.motivo
    )
    try:
        db.execute(newCita)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500,detail=f"Error al Registrar la Cita : {str(e)}")

    return {"mensaje": "Paciente registrado exitosamente"}





