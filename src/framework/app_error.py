from fastapi import HTTPException
from typing import Any
import json

class AppError(HTTPException):
    def __init__(
        self,
        class_pointer: Any,
        message: str,
        details: dict[str, Any] = {},
        status_code: int = 400,
    ) -> None:
        class_name = class_pointer.__class__.__name__

        error_detail = {
            "error": message,
            "details": details,
            "class": class_name,
        }
        print(f"[AppError] (status {status_code}):")
        print(json.dumps(error_detail, indent=3, ensure_ascii=False))

        super().__init__(
            status_code=status_code,
            detail={"error": message, "details": details, "class": class_name},
        )
        
