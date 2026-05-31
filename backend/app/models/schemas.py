from pydantic import BaseModel, Field
from typing import Optional, Any
from enum import Enum


class DataSourceType(str, Enum):
    FILE = "file"
    URL = "url"
    API = "api"


class DataUploadResponse(BaseModel):
    dataset_id: str
    filename: str
    row_count: int
    columns: list[str]
    preview: list[dict[str, Any]]


class UrlImportRequest(BaseModel):
    url: str = Field(..., description="Public URL to a CSV or JSON file")


class ApiImportRequest(BaseModel):
    url: str = Field(..., description="API endpoint URL")
    method: str = Field("GET", description="HTTP method (GET or POST)")
    headers: Optional[dict[str, str]] = Field(None, description="Optional HTTP headers")
    body: Optional[dict[str, Any]] = Field(None, description="Optional JSON body for POST requests")
    response_path: Optional[str] = Field(
        None,
        description="Dot-separated path to extract data from nested JSON (e.g., 'data.results')",
    )


class AgentQueryRequest(BaseModel):
    question: str = Field(..., description="Natural language question about the dataset")
    dataset_id: str = Field(..., description="ID of the dataset to analyze")


class SSEEvent(BaseModel):
    event: str
    data: dict[str, Any]


class AgentError(BaseModel):
    message: str
    detail: Optional[str] = None
