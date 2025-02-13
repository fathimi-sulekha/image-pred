import time
import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.endpoints import router as image_router

logger = logging.getLogger("app")
logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware for logging request details."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.2f}s")
    return response

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handles uncaught exceptions gracefully."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

app.include_router(image_router)

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)
 
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)