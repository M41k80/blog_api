import os
import shutil
import uuid
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from app.services.file_storage import save_uploaded_file

router = APIRouter(prefix="/uploads", tags=["uploads"])

MEDIA_DIR = "app/media/"

@router.post("/bytes")
async def upload_bytes(file: bytes = File(...)):
    return {
        "filename": "archivo_subido",
        "size_bytes": len(file)
    }


@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    return {
        "filename": file.filename,
        "content_type": file.content_type,
    }
    
    
@router.post("/save")
async def save_file(file: UploadFile = File(...)):
    saved = save_uploaded_file(file)
    
    return {
        "filename": saved["filename"],
        "content_type": saved["content_type"],
        "url": saved["url"],
        # "size": saved["size"],
        # "chunks_size_used": saved["chunks_size_used"],
        # "chunk_calls": saved["chunk_calls"],
        # "chunk_sizes_sample": saved["chunk_sizes_sample"]
    }
    