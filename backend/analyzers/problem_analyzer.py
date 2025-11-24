import google.generativeai as genai
import json
from . import config
from . import utils
from . import prompts

genai.configure(api_key=config.GOOGLE_API_KEY)


async def analyze_problem(problem_statement: str) -> dict:
    """Analyze problem statement to extract requirements and expected structure"""
    
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    prompt = f"{prompts.ANALYZE_PROBLEM_PROMPT}\n\nProblem Statement:\n{problem_statement}"
    response = model.generate_content(prompt)
    print("Problem analysis response:", response.text)
    
    result = utils.parse_json_response(response.text)
    return result
