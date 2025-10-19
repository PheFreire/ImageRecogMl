from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from fastapi.staticfiles import StaticFiles
from typing import Any, Dict
from fastapi import FastAPI
import uvicorn
import os

from app.predict.model_factory import predict
from app.utils.img_normalization import normalization
from app.utils.b64_serializer import B64Serializer

ROOT = os.getenv("ROOT_PATH", os.getcwd())
TEMPLATES_DIR = os.path.join(ROOT, "templates")
STATIC_DIR = os.path.join(ROOT, "static")

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)

app = FastAPI(title="Pixel Art ML")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    template = env.get_template("index.html")
    return HTMLResponse(template.render())

@app.post("/predict", response_class=JSONResponse)
async def vectorize(payload: Dict[str, Any]) -> JSONResponse:
    b64 = payload.get("imageDataURL", "")
    img = normalization(
        img=B64Serializer().to_gray_nd_array(b64),
        resize=(64, 64),
        binarize=True, 
        black_background=True
    )
    
    return JSONResponse(predict(img))

if __name__ == '__main__':
    API_HOST = os.getenv("API_HOST", "127.0.0.1")
    API_PORT = os.getenv("API_PORT", "3333")

    uvicorn.run(
        app='main:app',
        host=API_HOST,
        port=int(API_PORT),
        reload=True
    )

