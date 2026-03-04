from typing import BinaryIO
import logging
import json
from pathlib import Path

from google import genai
from google.genai import types, errors

from store.plant_health.domain.entities import PlantHealthReport
from store.plant_health.domain.interfaces import PlantHealthService
from store.plant_health.domain.exceptions import LowConfidenceError, InvalidPlantImageError, ServiceUnavailableError

class GeminiPlantHealthService(PlantHealthService):
    """
    Production implementation of PlantHealthService using Google GenAI SDK (v2).
    """

    def __init__(self, api_key: str, model_name: str = "gemini-3-flash-preview", fallback_model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
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
            # Handle rate limit (429) or service overload (503) — try fallback model
            is_rate_limit = e.code == 429 or (hasattr(e, 'status_code') and e.status_code == 429)
            is_overloaded = e.code == 503 or (hasattr(e, 'status_code') and e.status_code == 503)

            if is_rate_limit or is_overloaded:
                reason = "Quota Exceeded" if is_rate_limit else "Service Overloaded (503)"
                logging.warning(f"Gemini primary model failed ({reason}), falling back to {self.fallback_model_name}")
                try:
                    return self.__call_gemini_api(image_bytes, use_fallback=True)
                except (errors.APIError, errors.ClientError) as fb_error:
                    if fb_error.code in (429, 503) or (hasattr(fb_error, 'status_code') and fb_error.status_code in (429, 503)):
                        raise ServiceUnavailableError(
                            "El servicio de análisis de IA está temporalmente saturado. Por favor intenta en unos segundos."
                        ) from fb_error
                    logging.error(f"Fallback model also failed: {fb_error}")
                    raise LowConfidenceError("Service is temporarily busy. Please try again later.") from fb_error
                except Exception as fb_ex:
                    logging.error(f"Unexpected error with fallback model: {fb_ex}")
                    raise LowConfidenceError("An unexpected error occurred during fallback analysis.") from fb_ex
            
            logging.error(f"Gemini Client/API Error: {e}")
            raise e

        except OSError as e:
            # Network-level error (DNS failure, no connection, etc.)
            logging.error(f"Network error reaching Gemini API: {e}")
            raise ServiceUnavailableError(
                "No se pudo conectar al servicio de análisis de IA. Verifica tu conexión a internet."
            ) from e

        except Exception as e:
            logging.error(f"Unexpected Error during photo analysis: {e}")
            raise LowConfidenceError("An unexpected error occurred during analysis.") from e

    def __call_gemini_api(self, image_data: bytes, use_fallback: bool = False) -> PlantHealthReport:
        """
        Direct communication with the model and mapping to PlantHealthReport.
        """
        prompt = self.__get_prompt()
        target_model = self.fallback_model_name if use_fallback else self.model_name

        try:
            response = self.client.models.generate_content(
                model=target_model,
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
            
            # Extract and validate is_plant
            is_plant = raw_data.pop("is_plant", True)
            if not is_plant:
                raise InvalidPlantImageError("La imagen no contiene una planta clara")

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