from fastapi import FastAPI
from fastapi import Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException,status,Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from passwords import  hash_passwords, verify_password # retorna verify un resultado booleano 
from database import SessionLocal ,Base, engine, metadata, get_db
from models import reflect_tables, metadata 
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app= FastAPI()

origins = [
   
    "http://localhost:3000",  # Dirección del cliente React
    "http://127.0.0.1:3000", # Dirección donde se ejecuta React en desarrollo
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


class OAuth2PasswordRequestFormEmail(OAuth2PasswordRequestForm):
    def __init__(self, email: str = Form(...), password: str = Form(...)):
        super().__init__(username=email, password=password)

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestFormEmail = Depends(), db: Session = Depends(get_db)):
    # Buscar usuario por email
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
    return {"access_token": access_token, "token_type": "bearer", "rol": rol}


class UsuarioCreate(BaseModel):
    username:str
    email: str
    password: str

# Endpoint para registrar un usuario
@app.post("/register")
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe por correo electrónico
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
        db.execute(nuevo_usuario)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al registrar el usuario")

    return {"mensaje": "Usuario registrado exitosamente"}
