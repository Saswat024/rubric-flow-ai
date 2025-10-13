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
    """Evaluate flowchart using gemini-2.5-flash-lite with image input"""

    system_prompt = """You are an expert flowchart evaluator.Analyze the uploaded flowchart image and evaluate it according to the following rubrics:
1. Start/End Presence (10 pts) – The flowchart includes clearly defined start and end terminal nodes in the correct shapes (rounded rectangles or ovals).
2. Decision Nodes (30 pts) – Decision points use diamond shapes correctly and contain clear, labeled branches (e.g., “Yes” / “No”).
3. Completeness (30 pts) – The flowchart captures all major steps of the intended process or algorithm without missing links or logic gaps.
4. Flow Direction (20 pts) – The flow proceeds logically and consistently (preferably top-to-bottom or left-to-right) with properly connected arrows.
5. Label Clarity (10 pts) – All shapes and connections have legible, descriptive text for easy understanding.

Output Format
Return only a valid JSON object (no additional explanation or commentary) in this exact structure:
{
  "total_score": <number between 0 and 100>,
  "breakdown": [
    {
      "criterion": "<string>",
      "score": <number>,
      "max_score": <number>,
      "feedback": "<short justification or comment>"
    }
  ],
  "feedback": [
    "<3–5 concise, actionable feedback items with emojis (✅ strengths, ⚠️ issues, 💡 suggestions)>"
  ]
}
Evaluation Guidelines

-> Base your assessment solely on the visual content of the flowchart image.
-> Assign scores objectively according to how well each rubric is visually represented.
-> Provide specific reasons for each rubric score in breakdown.feedback.
-> Include 3–5 clear, actionable feedback points in the main feedback array.
Use emojis consistently:

✅ for correct or strong elements
⚠️ for errors or missing elements
💡 for suggested improvements
"""

    # Decode base64 image
    image_data = base64_image.split(',')[1] if ',' in base64_image else base64_image
    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes))

    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    prompt = f"{system_prompt}\n\nEvaluate this flowchart based on the rubrics. Provide detailed scoring and feedback."
    response = model.generate_content([prompt, image])
    print("Raw response:", response.text)
    result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
    return result
