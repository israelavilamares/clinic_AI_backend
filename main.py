from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
app= FastAPI()

origins = [
    "http://localhost:3000",  # Dirección donde se ejecuta React en desarrollo
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permite solicitudes desde React
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los encabezados
)


@app.get("/")
def read_root():
    return {"Hello": "World"}