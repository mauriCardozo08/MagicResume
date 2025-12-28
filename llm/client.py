import os
from google import genai

def _get_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set. "
            "Please set it before running the application."
        )
    return api_key

client = genai.Client(api_key=_get_api_key())

def call_gemini(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        
        if not hasattr(response, "text") or not response.text:
            print(f"Error: Gemini API returned empty response.")
            print(f"Full response object: {response}")
            raise RuntimeError("Gemini API returned an empty response")
        
        return response
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        raise