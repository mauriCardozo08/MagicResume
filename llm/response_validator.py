import json
from typing import Dict, Any


def validate_model_response(response_text: str) -> Dict[str, Any]:
    response_text = response_text.strip()
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    elif response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    response_text = response_text.strip()
    
    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse Gemini response as JSON: {e}\nRaw response: {response_text}")

    if not isinstance(parsed, dict):
        raise RuntimeError("Response is not a JSON object")

    if "company_name" not in parsed:
        raise RuntimeError("Response is missing required key: 'company_name'")
    
    if not isinstance(parsed.get("company_name"), str):
        raise RuntimeError("'company_name' must be a string")
    
    if "role_replacements" not in parsed or "skill_replacements" not in parsed:
        raise RuntimeError("Response is missing required keys: 'role_replacements' or 'skill_replacements'")

    role_replacements = parsed.get("role_replacements", [])
    skill_replacements = parsed.get("skill_replacements", [])

    if len(role_replacements) == 0 and len(skill_replacements) == 0:
        raise RuntimeError("No replacements suggested by Gemini. No changes will be made to the document.")

    return parsed

