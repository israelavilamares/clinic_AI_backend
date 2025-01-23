# models.py
from database import Base, engine, metadata
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


class Cita(BaseModel):
    id_paciente: int
    fecha: str
    hora: str
    motivo: str

class CitaUser(BaseModel):
    motivo: str
    estado: str
    
    class Config:
        from_attributes = True 


class UpdateCitaRequest(BaseModel):
    motivo: Optional[str] = None
    estado: Optional[str] = None
