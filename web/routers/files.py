from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse
import os


router = APIRouter()
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
ATTACH_DIR = os.path.join(BASE_DIR, "attachs")


@router.get("/file/{filename}")
async def get_file(filename: str, request: Request):
    client_ip = request.client.host
    if client_ip not in ['tgbot']:
        raise HTTPException(status_code=403, detail="Access denied")

    file_path = os.path.join(ATTACH_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)
