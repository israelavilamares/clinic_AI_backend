# models.py
from h11 import Data
from sqlalchemy import DATE
from schemas.database import Base, engine, metadata
from pydantic import BaseModel
from typing import Optional

# Reflejar las tablas de la base de datos
def reflect_tables():
    metadata.reflect(bind=engine)  # Esto obtiene todas las tablas de la base de datos
    for table_name, table in metadata.tables.items():
        # Crea un modelo de SQLAlchemy para cada tabla reflejada
        print(f"Reflejando tabla: {table_name}")
        
        globals()[table_name] = type(table_name, (Base,), {
            '__tablename__': table_name,
            '__table__': table
        })

# Llamar a la función de reflección se ven todas las tablas[pacientes,medicos,usuarios]
reflect_tables()

class meDoctor(BaseModel):
  
    especialidad :str | None = None
    cedula_profesional: str | None = None
    telefono_contacto: str | None = None
    id_usuario:int  | None = None
    is_delete: bool | None = None
    nombre: str | None = None


class CitaD(BaseModel):
    id_paciente: int
    fecha: str
    hora: str
    motivo: str
    id: int
    estado: str
    id_medico: int

class Cita(BaseModel):
    id_paciente: int
    fecha: str
    hora: str
    motivo: str
   # id: int
  #  estado: str
    id_medico: int

class CitaUser(BaseModel):
    motivo: str
    estado: str
    
    class Config:
        from_attributes = True 


class UpdateCitaRequest(BaseModel):
    motivo: Optional[str] = None
    estado: Optional[str] = None

class Expe(BaseModel):
    #puede faltar traer al id
    nombre_paciente: str
    telefono: str
    cirugia: str
    enfermedad: str
    alergia: str
    tratamientos: str
    id_paciente: int

#es lo que tiene que devolver auth
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol:str
    id: int


class ExpedienteCreate(BaseModel):
    nombre_paciente:str | None = None
    telefono: str | None = None
    cirugia:str | None = None
    enfermedad: str | None = None 
    tratamientos: str | None = None  
    alergia:str | None = None
    id_paciente: int | None = None

class PutexpCreate(BaseModel):
    nombre_paciente:str | None = None
    telefono: str | None = None
    cirugia:str | None = None
    enfermedad: str | None = None 
    tratamientos: str | None = None  
    alergia:str | None = None

class medico(BaseModel):
    id_medico: int | None = None
    nombre: str | None = None

class Paciente_(BaseModel):  
    id_paciente: int
    sexo: str
    direccion: str
    is_delete: bool
    nombre: str
    tel: int

class UsuarioCreate(BaseModel):
    username:str
    email: str
    password: str

class Paciente(BaseModel):
    date: str
    sexo: str
    id_usuario : int  
    address : str
    name: str
    tel: str                                    