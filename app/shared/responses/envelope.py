from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel
from fastapi.responses import JSONResponse

class APIResponseEnvelope(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = ""
    request_id: Optional[str] = ""
    timestamp: str = ""
    errors: Optional[Any] = None

def wrap_response(
    success: bool,
    data: Optional[Any] = None,
    message: Optional[str] = "",
    request_id: Optional[str] = "",
    errors: Optional[Any] = None,
    status_code: int = 200
) -> JSONResponse:
    """Wraps responses inside a unified API response envelope."""
    serializable_data = data
    if hasattr(data, "model_dump"):
        serializable_data = data.model_dump(mode="json")
    elif isinstance(data, list):
        serializable_data = [item.model_dump(mode="json") if hasattr(item, "model_dump") else item for item in data]

    content = {
        "success": success,
        "data": serializable_data,
        "message": message,
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "errors": errors
    }
    return JSONResponse(status_code=status_code, content=content)
