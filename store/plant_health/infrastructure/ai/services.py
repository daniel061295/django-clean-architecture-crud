from typing import BinaryIO
import logging
import json
from pathlib import Path

from google import genai
from google.genai import types, errors

from store.plant_health.domain.entities import PlantHealthReport
from store.plant_health.domain.interfaces import PlantHealthService
from store.plant_health.domain.exceptions import LowConfidenceError

class GeminiPlantHealthService(PlantHealthService):
    """
    Production implementation of PlantHealthService using Google GenAI SDK (v2).
    """

    def __init__(self, api_key: str, model_name: str = "gemini-3-flash-preview"):
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key)

    def analyze_photo(self, photo: BinaryIO) -> PlantHealthReport:
        """
        Analyzes the photo with retry logic and confidence validation.
        """
        # Ensure pointer is at the start if buffer is reused
        photo.seek(0)
        image_bytes = photo.read()

        try:
            report = self.__call_gemini_api(image_bytes)
            return report

        except (errors.APIError, errors.ClientError) as e:
            # Handle specific API Client Errors (like 429)
            if e.code == 429 or (hasattr(e, 'status_code') and e.status_code == 429):
                logging.error(f"Gemini API Quota Exceeded: {e}")
                raise LowConfidenceError("Service is temporarily busy (Quota Exceeded). Please try again later.") from e
            
            logging.error(f"Gemini Client/API Error: {e}")
            raise e

        except Exception as e:
            logging.error(f"Unexpected Error during photo analysis: {e}")
            raise LowConfidenceError("An unexpected error occurred during analysis.") from e

    def __call_gemini_api(self, image_data: bytes) -> PlantHealthReport:
        """
        Direct communication with the model and mapping to PlantHealthReport.
        """
        prompt = self.__get_prompt()    

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=prompt),
                            types.Part.from_bytes(data=image_data, mime_type="image/jpeg"),
                        ],
                    )
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.4,
                ),
            )
            
            if not response.text:
                raise ValueError(f"Empty response from API. Status: {getattr(response, 'status', 'Unknown')}")

            raw_data = json.loads(response.text)
            return PlantHealthReport(**raw_data)

        except (json.JSONDecodeError, KeyError) as e:
            logging.error(f"Error parsing Gemini response: {e}")
            raise ValueError(f"AI returned invalid format: {str(e)}") from e
        except Exception as e:
            logging.error(f"Unexpected Error during Gemini API call: {e}")
            raise e

    def __get_prompt(self) -> str:
        """
        Get the prompt from the file.
        """
        prompt_path = Path(__file__).parent / "prompts" / "get_plant_patology.md"
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read()
        return prompt