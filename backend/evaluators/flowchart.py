from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def evaluate_flowchart(base64_image: str):
    """Evaluate flowchart using GPT-4 Vision"""

    system_prompt = """You are an expert flowchart evaluator. Analyze flowcharts based on these rubrics:
1. Start/End Presence (10 pts): Proper terminal nodes
2. Decision Nodes (30 pts): Correct use of decision diamonds with branches
3. Completeness (30 pts): All necessary steps included
4. Flow Direction (20 pts): Proper arrows and logical flow
5. Label Clarity (10 pts): Clear, descriptive labels

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
  "feedback": ["string array of 3-5 actionable feedback items with emojis"]
}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Evaluate this flowchart based on the rubrics. Provide detailed scoring and feedback.",
                    },
                    {"type": "image_url", "image_url": {"url": base64_image}},
                ],
            },
        ],
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return result
