from fastapi import APIRouter, File, UploadFile, HTTPException

from app.models.schemas import (
    DataUploadResponse,
    UrlImportRequest,
    ApiImportRequest,
)
from app.services import data_loader

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("/upload", response_model=DataUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a CSV or JSON dataset."""
    if not file.filename:
        raise HTTPException(400, "No filename provided")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ("csv", "json"):
        raise HTTPException(400, "Only CSV and JSON files are supported")

    content = await file.read()
    try:
        result = data_loader.load_from_file(content, file.filename)
    except Exception as e:
        raise HTTPException(400, str(e))

    return DataUploadResponse(
        dataset_id=result["dataset_id"],
        filename=result["filename"],
        row_count=result["row_count"],
        columns=result["columns"],
        preview=result["preview"],
    )


@router.post("/url", response_model=DataUploadResponse)
async def import_from_url(request: UrlImportRequest):
    """Import a dataset from a public URL."""
    try:
        result = data_loader.load_from_url(request.url)
    except Exception as e:
        raise HTTPException(400, f"Failed to fetch URL: {e}")

    return DataUploadResponse(
        dataset_id=result["dataset_id"],
        filename=result["filename"],
        row_count=result["row_count"],
        columns=result["columns"],
        preview=result["preview"],
    )


@router.post("/api", response_model=DataUploadResponse)
async def import_from_api(request: ApiImportRequest):
    """Import a dataset from an API endpoint."""
    try:
        result = data_loader.load_from_api(
            url=request.url,
            method=request.method,
            headers=request.headers,
            body=request.body,
            response_path=request.response_path,
        )
    except Exception as e:
        raise HTTPException(400, f"Failed to fetch API: {e}")

    return DataUploadResponse(
        dataset_id=result["dataset_id"],
        filename=result["filename"],
        row_count=result["row_count"],
        columns=result["columns"],
        preview=result["preview"],
    )
