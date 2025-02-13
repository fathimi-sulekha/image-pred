import base64
import json
import logging
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from typing import Optional
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# OpenAI client initialization
client = OpenAI(api_key=settings.OPENAI_API_KEY)

print(f"🔑 OpenAI API Key: {settings.OPENAI_API_KEY}")  # Debugging
# Define expected AI response structure
class PartInspectionResult(BaseModel):
    recognized_part: str
    defect_status: str
    defect_type: Optional[str] = None
    confidence: float

class OpenAIService:
    async def call_model(self, file_content: bytes) -> dict:
        """Calls OpenAI API with an image and returns structured JSON output."""
        
        print("📢 Calling OpenAI model now...")
        logger.debug("📢 Calling OpenAI model now...")

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
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages
            )

            result_text = response.choices[0].message.content.strip()

            print(f"✅ Raw OpenAI Response: {result_text}")
            logger.debug(f"✅ Raw OpenAI Response: {result_text}")

            # Remove Markdown JSON formatting if present
            if result_text.startswith("```json"):
                result_text = result_text.strip("```json").strip("```")

            # Validate and parse AI response
            result_obj = PartInspectionResult.parse_raw(result_text)
            print(f"✅ Successfully Parsed Response: {result_obj.dict()}")
            logger.info(f"✅ Successfully Parsed Response: {result_obj.dict()}")

            return result_obj.dict()

        except ValidationError as e:
            print(f"❌ OpenAI response validation failed: {e}")
            logger.error(f"❌ OpenAI response validation failed: {e}")
            return {"error": "Failed to parse AI response"}

        except Exception as e:
            print(f"❌ Unexpected OpenAI API error: {e}")
            logger.error(f"❌ Unexpected OpenAI API error: {e}", exc_info=True)
            return {"error": "AI model call failed"}
