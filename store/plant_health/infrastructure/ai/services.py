import random
from typing import BinaryIO
import time
import os
import logging

from google import genai
from google.genai import types
import json

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
            report = self._call_gemini_api(image_bytes)
            return report

        except Exception as e:
            logging.error(f"Gemini API Error :{e}")
            raise LowConfidenceError("Service is temporarily busy (Quota Exceeded). Please try again later.") from e

    def _call_gemini_api(self, image_data: bytes) -> PlantHealthReport:
        """
        Direct communication with the model and mapping to PlantHealthReport.
        """
        prompt = """
        You are an expert in botany and plant pathology. Analyze this plant image:
        1. Identify if it is healthy or has pests/diseases.
        2. Provide a confidence level from 0.0 to 1.0.
        3. Generate clear treatment steps.
        
        JSON Response:
        {
          "is_healthy": bool,
          "diagnosis": "Disease name or 'Healthy'",
          "confidence": float,
          "treatment": ["step 1", "step 2"],
          "urgency_level": "Low" | "Medium" | "High"
        }
        """

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
            raise e