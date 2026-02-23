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