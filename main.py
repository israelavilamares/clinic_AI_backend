import os
from fastapi import FastAPI
from fastapi import Form, Query, Body, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException,status,Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Annotated
from sqlalchemy import column, insert, text, Table, select, delete ,update as sqlalchemy_update, join
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
import uvicorn
#import doctor


from schemas.database import SessionLocal ,Base, engine, metadata, get_db
from schemas.schema import PutexpCreate, reflect_tables, metadata,Cita,CitaUser,UpdateCitaRequest,Expe,ExpedienteCreate,medico,Paciente_,UsuarioCreate,Paciente
import logging
from routers import auth,paciente,doctor



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





#api_v1_router = APIRouter(prefix="/api/v1")

# Incluir el router de doctores bajo el prefijo /api/v1
#api_v1_router.include_router(doctor.router)

# Registrar el router principal en la app
#app.include_router(api_v1_router)
app.include_router(auth.router)
app.include_router(paciente.router)
app.include_router(doctor.router)




if __name__=="__main__":
    uvicorn.run("main:app",port=8000,reload=True)