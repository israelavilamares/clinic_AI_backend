import os
from dotenv import load_dotenv
from sqlalchemy import create_engine,   MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from urllib.parse import quote_plus

load_dotenv()

host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database_name = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

encoded_password = quote_plus(password)

# Validar que todas las variables necesarias estén definidas
if not all([host, port, database_name, user, password]):
    raise ValueError("Faltan una o más variables de entorno necesarias para la configuración de la base de datos.")


DATABASE_URL = f"postgresql://{user}:{encoded_password}@{host}:{port}/{database_name}"

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL)

# Crear la instancia de la base
metadata = MetaData()

# Usar la reflexión para reflejar las tablas de la base de datos existente
Base = declarative_base(metadata=metadata)

# Crear una fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependencia para obtener una sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

