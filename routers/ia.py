from fastapi import APIRouter
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from typing import Annotated

router = APIRouter(tags=["IA"])

@router.post("/paciente/file/")
async def file():
    pass
    #return {"mensaje":"Expediente creado correctamente"}

