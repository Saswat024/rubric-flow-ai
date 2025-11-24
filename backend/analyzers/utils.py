import json
import re

def parse_json_response(response_text: str) -> dict:
    """
    Clean and parse JSON response from Gemini.
    Removes markdown code blocks and handles common formatting issues.
    """
    try:
        cleaned_text = response_text.strip()
        # Remove markdown code blocks if present
        if "```" in cleaned_text:
            cleaned_text = re.sub(r"```json\s*", "", cleaned_text)
            cleaned_text = re.sub(r"```\s*", "", cleaned_text)
        
        cleaned_text = cleaned_text.strip()
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Original text: {response_text}")
        raise e
