from framework.app_error import AppError
from numpy.typing import NDArray
from PIL import Image
import numpy as np
import base64
import io

class B64Serializer:
    def to_gray_nd_array(self, b64: str) -> NDArray:
        if not b64.startswith("data:image"):
            raise AppError(
                self, 
                message="invalid b64 data URL",
                details={"error": "Invalid data URL"}, 
                status_code=500
            )
    
        try:
            b64_img = base64.b64decode(b64.removeprefix("data:image/png;base64,"))
        except Exception as e:
            raise AppError(
                self, 
                message="could not process b64",
                details={"error": f"Failed to decode image: {e}"}, 
                status_code=500
            )
    
        try:
            img = (
                Image.open(io.BytesIO(b64_img))
                .convert("L")
                .resize((256, 256), Image.Resampling.LANCZOS)
            )
            return np.array(img, dtype=np.uint8)
        except Exception as e:
            raise AppError(
                self, 
                message="could not serialize img",
                details={"error": f"Failed to open image: {e}"}, 
                status_code=500
            )
            
