import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routers import auth,paciente,doctor,adm,ia

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

# Routers
app.include_router(auth.router)
app.include_router(paciente.router)
app.include_router(doctor.router, prefix="/doctor")
app.include_router(adm.router, prefix="/adm")
app.include_router(ia.router, prefix="/ia")



if __name__=="__main__":
    uvicorn.run("main:app",port=8000,reload=True)