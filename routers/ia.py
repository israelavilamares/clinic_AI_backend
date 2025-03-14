import io
import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from typing import Annotated
from schemas.database import get_db, metadata
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import insert

router = APIRouter(tags=["Ia"])

@router.post("/paciente/archivo/")
async def create_file(file: UploadFile, db: Session = Depends(get_db)):
    try: 
        file_content = await file.read()
        stmt = insert(metadata.tables["documents"]).values(file=file_content)
        db.execute(stmt)
        db.commit()
        return {"ok": True}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error saving file")
    

@router.get("/paciente/archivo/{file_id}")
async def get_file(file_id: int, db: Session = Depends(get_db)):
    try:
        # Query the file from the database
        stmt = metadata.tables["documents"].select().where(metadata.tables["documents"].c.id == file_id)
        result = db.execute(stmt).mappings().fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Assuming the column name is "file"
        file_content = result["file"]  
        # Convert bytes to a stream
        pdf =  StreamingResponse(io.BytesIO(file_content), media_type="application/octet-stream",
                                 headers={"inline": f'attachment; filename="file_{file_id}"'})
        return pdf

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error retrieving file")

#-----------------------------------------------------------------------------
#llamar al modelo para la descripcion de los resultados de si es diabetes o no
#------------------------------------------------------------------------------
