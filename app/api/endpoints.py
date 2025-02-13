from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from app.controller.image_controller import process_image_request

router = APIRouter()

@router.post("/process-image/")
async def process_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(None)
):
    """Processes an uploaded image, calls OpenAI, caches result."""
    
    if file is None:
        raise HTTPException(status_code=400, detail="File must be provided.")
    
    response = await process_image_request(background_tasks, file)
    return JSONResponse(response)
