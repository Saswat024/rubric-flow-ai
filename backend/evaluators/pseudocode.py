import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("GOOGLE_API_KEY")
print(f"Pseudocode API Key loaded: {'YES' if api_key else 'NO'}")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")
genai.configure(api_key=api_key)


async def evaluate_pseudocode(code: str):
    """Evaluate pseudocode using gemini-pro"""

    system_prompt = """You are an expert pseudocode evaluator. Analyze pseudocode based on these rubrics:
1. Correctness (50 pts): Logic is sound and achieves intended purpose
2. Edge Case Handling (20 pts): Handles special cases and error conditions
3. Clarity (15 pts): Clear variable names, proper structure, readable
4. Complexity (15 pts): Efficient algorithm, appropriate complexity

Return a JSON object with:
{
  "total_score": number (0-100),
  "breakdown": [
    {
      "criterion": "string",
      "score": number,
      "max_score": number,
      "feedback": "string"
    }
  ],
  "feedback": ["string array of 3-5 actionable feedback items with emojis (✅, ⚠️, 💡)"]
}"""

    model = genai.GenerativeModel("gemini-2.5-pro")
    prompt = f"{system_prompt}\n\nEvaluate this pseudocode based on the rubrics:\n\n{code}"
    response = model.generate_content(prompt)
    print("Raw response:", response.text)
    result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
    return result
