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
    """Evaluate pseudocode using gemini-2.5-flash-lite"""

    system_prompt = """You are an expert pseudocode evaluator. Evaluate the given pseudocode according to the following rubrics:
1. Correctness (50 pts) – The pseudocode’s logic is sound, complete, and correctly implements the intended task or algorithm.
2. Edge Case Handling (20 pts) – The pseudocode considers special or boundary cases (e.g., empty inputs, invalid data, zero values, etc.) and prevents runtime or logical errors
3. Clarity (15 pts) – The pseudocode uses meaningful variable names, clear control structures, and consistent indentation; overall readability is high.
4. Complexity (15 pts) – The algorithm demonstrates efficiency and appropriate time/space complexity for the problem; avoids unnecessary operations.

Output Format
Return the evaluation strictly as a JSON object with the following structure:
{
  "total_score": <number between 0 and 100>,
  "breakdown": [
    {
      "criterion": "<string>",
      "score": <number>,
      "max_score": <number>,
      "feedback": "<string>"
    }
  ],
  "feedback": [
    "<string array of 3-5 actionable feedback items with emojis (✅, ⚠️, 💡)>"
  ]
}
Additional Guidelines

-> Be objective and concise in scoring.
-> Include specific reasons for each criterion’s score.
-> In the feedback array, provide actionable suggestions for improvement (not just restating issues).
Use the emojis as follows:
✅ for strengths
⚠️ for issues or weaknesses
💡 for suggestions or enhancements
"""

    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    prompt = f"{system_prompt}\n\nEvaluate this pseudocode based on the rubrics:\n\n{code}"
    response = model.generate_content(prompt)
    print("Raw response:", response.text)
    result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
    return result
