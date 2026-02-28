# backend\api\main.py

from fastapi import FastAPI
from mangum import Mangum
from api.routes import router
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SamvaadAI API",
    version="1.0.0",
    root_path=""
)

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}

handler = Mangum(app)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)