from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def evaluate_pseudocode(code: str):
    """Evaluate pseudocode using GPT-4"""

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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Evaluate this pseudocode based on the rubrics:\n\n{code}",
            },
        ],
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return result
