import google.generativeai as genai
import os
import json
import base64
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("GOOGLE_API_KEY")
print(f"Flowchart API Key loaded: {'YES' if api_key else 'NO'}")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")
genai.configure(api_key=api_key)


async def evaluate_flowchart(base64_image: str):
    """Evaluate flowchart using gemini-1.5-pro with image input"""

    system_prompt = """You are an expert flowchart evaluator. Analyze flowcharts based on these rubrics:
1. Start/End Presence (10 pts): Proper terminal nodes
2. Decision Nodes (30 pts): Correct use of decision diamonds with branches
3. Completeness (30 pts): All necessary steps included
4. Flow Direction (20 pts): Proper arrows and logical flow
5. Label Clarity (10 pts): Clear, descriptive labels

Return ONLY a valid JSON object with:
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

    # Decode base64 image
    image_data = base64_image.split(',')[1] if ',' in base64_image else base64_image
    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes))
    
    model = genai.GenerativeModel('gemini-2.5-pro')
    prompt = f"{system_prompt}\n\nEvaluate this flowchart based on the rubrics. Provide detailed scoring and feedback."
    response = model.generate_content([prompt, image])
    print("Raw response:", response.text)
    result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
    return result
