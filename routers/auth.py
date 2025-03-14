import os
from dotenv import load_dotenv
from fastapi import Form, HTTPException,status,Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from schemas.database import get_db ,metadata
from schemas.schema import Token, UsuarioCreate
from services.auth_hash import hash_passwords, verify_password  # your helper functions

router = APIRouter(tags=["Autenticación"])

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 50

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class OAuth2PasswordRequestFormEmail(OAuth2PasswordRequestForm):
    def __init__(self, email: str = Form(...), password: str = Form(...)):
        super().__init__(username=email, password=password)

@router.post("/login", response_model=Token)
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


# Endpoint para registrar un usuario
@router.post("/register")
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

@router.post("/olvidar-password")
def forgetPassword(email: str, db: Session = Depends(get_db)):
    user = db.query(metadata.tables["usuario"]).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=400, detail="El email no existe")
    # Enviar email con el link para cambiar la contraseña

    return {"mensaje": "Email enviado con éxito"}