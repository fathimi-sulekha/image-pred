import base64
import logging
import openai
import os
from pydantic import BaseModel, ValidationError
from typing import Optional
from app.core.config import settings


# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Set the OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

# ----- Existing function for image processing -----
class PartInspectionResult(BaseModel):
    recognized_part: str
    defect_status: str
    defect_type: Optional[str] = None
    confidence: float

class OpenAIService:
    async def call_model(self, file_content: bytes) -> dict:
        """Calls OpenAI API with an image and returns structured JSON output."""
        print("📢 Calling OpenAI model now (image)...")
        logger.debug("📢 Calling OpenAI model now (image)...")
        base64_image = base64.b64encode(file_content).decode("utf-8")
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Analyze this automobile part and return a JSON object with these fields:\n"
                            "- recognized_part (string): Name of the automobile part\n"
                            "- defect_status (string): 'Defective' or 'Not Defective'\n"
                            "- defect_type (string or null): If defective, either 'Manufacturing Defect' or 'Customer Abuse'; otherwise, null\n"
                            "- confidence (number): A value between 0 and 1\n\n"
                            "Return only valid JSON, with no extra text."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=messages
            )
            result_text = response.choices[0].message.content.strip()
            print(f"✅ Raw OpenAI Response (image): {result_text}")
            logger.debug(f"✅ Raw OpenAI Response (image): {result_text}")
            if result_text.startswith("```json"):
                result_text = result_text.strip("```json").strip("```")
            result_obj = PartInspectionResult.parse_raw(result_text)
            print(f"✅ Parsed Response (image): {result_obj.dict()}")
            logger.info(f"✅ Parsed Response (image): {result_obj.dict()}")
            return result_obj.dict()
        except ValidationError as e:
            print(f"❌ OpenAI response validation failed (image): {e}")
            logger.error(f"❌ OpenAI response validation failed (image): {e}")
            return {"error": "Failed to parse AI response"}
        except Exception as e:
            print(f"❌ Unexpected OpenAI API error (image): {e}")
            logger.error(f"❌ Unexpected OpenAI API error (image): {e}", exc_info=True)
            return {"error": "AI model call failed"}

# ----- New function for text prompts using function calling -----
async def call_openai_for_text(prompt: str) -> dict:
    """
    Calls the OpenAI API with a text prompt and uses function calling to trigger 'get_weather'.
    """
    print("📢 Calling OpenAI model now (text)...")
    logger.debug("📢 Calling OpenAI model now (text)...")
    
    # Define the function schema for 'get_weather'
    functions = [
        {
            "name": "get_weather",
            "description": "Fetches weather information for a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and country, e.g., 'Boston, MA'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["location"]
            }
        }
    ]
    
    messages = [
        {"role": "user", "content": prompt}
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=messages,
            functions=functions,
            function_call="auto"  # Automatically decide whether to call a function
        )
        message = response.choices[0].message
        print("✅ Raw OpenAI Text Response:", message)
        logger.debug("✅ Raw OpenAI Text Response: %s", message)
        
        # Check if a function call was triggered
        if "function_call" in message:
            function_call = message["function_call"]
            print("✅ Function call details:", function_call)
            logger.info("✅ Function call details: %s", function_call)
            return {"function_call": function_call}
        else:
            return {"result": message.get("content", "")}
    except Exception as e:
        print(f"❌ Unexpected OpenAI API error (text): {e}")
        logger.error(f"❌ Unexpected OpenAI API error (text): {e}", exc_info=True)
        return {"error": "AI model call failed"}
