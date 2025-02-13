from fastapi import APIRouter, HTTPException
from app.dependencies.schema import TextRequest
from app.services.openai_services import call_openai_for_text
from app.weather import get_weather  # Assuming you have this function implemented

router = APIRouter()

@router.post("/process-text/")
async def process_text(request: TextRequest):
    """
    Processes a text prompt using OpenAI function calling.
    For example, you can ask "What's the weather like in Boston?"
    """
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    
    response = await call_openai_for_text(request.prompt)
    
    # If the response triggers a function call, process it
    if "function_call" in response:
        function_call = response["function_call"]
        if function_call.get("name") == "get_weather":
            arguments = function_call.get("arguments")
            # Call your get_weather function to process the request
            weather_result = get_weather(arguments)
            return {"result": weather_result}
    
    return response
