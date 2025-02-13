import logging
from fastapi import APIRouter, BackgroundTasks, UploadFile
from fastapi.logger import logger
from app.services.openai_services import OpenAIService
from app.services.redis_cache import RedisCache
from app.utils.helpers import generate_cache_key

# Initialize router and services
router = APIRouter()
openai_service = OpenAIService()
redis_cache = RedisCache()

logging.basicConfig(level=logging.DEBUG)

@router.post("/process-image/")
async def process_image_request(background_tasks: BackgroundTasks, file: UploadFile = None, blob_name: str = None):
    """Processes an image (uploaded file or from Azure blob), calls OpenAI, caches result, and stores data."""
    print("📢 process_image_request called!")
    logger.debug("📢 process_image_request called!")
    
    if file is None and blob_name is None:
        print("❌ Error: No file or blob_name provided!")
        return {"error": "Either 'file' or 'blob_name' must be provided."}
    
    if file:
        print(f"📂 Received uploaded file: {file.filename}")
        file_content = await file.read()
    else:
        print(f"📂 Processing Azure Blob: {blob_name}")
        return {"error": "Azure Blob processing removed from this version."}
    
    # Generate cache key (only use file content here)
    cache_key = generate_cache_key(file_content)
    print(f"🔑 Cache Key: {cache_key}")

    # Check Redis cache
    cached_result = await redis_cache.get_cache(cache_key)
    if cached_result and "error" not in cached_result:
        print(f"✅ Cache Hit: {cached_result}")
        return {"result": cached_result, "cached": True}
    else:
        print("⚠️ Cached response contained an error, ignoring cache...")

    print("⏳ Calling OpenAI Service...")
    try:
        response = await openai_service.call_model(file_content)
        print(f"✅ OpenAI Response: {response}")
        if "error" in response:
            print("❌ OpenAI returned an error!")
            return {"result": response, "cached": False}
        await redis_cache.set_cache(cache_key, response)
        print("🗄️ Cached OpenAI Response.")
        return {"result": response, "cached": False}
    except Exception as e:
        print(f"❌ Process Image Error: {e}")
        logger.error(f"❌ Process Image Error: {e}", exc_info=True)
        return {"error": str(e)}
