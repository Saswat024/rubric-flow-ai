import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")
genai.configure(api_key=api_key)


async def analyze_problem(problem_statement: str) -> dict:
    """Analyze problem statement to extract requirements and expected structure"""
    
    system_prompt = """You are an expert algorithm analyst. Analyze the given problem statement and extract key information that will help evaluate solutions.

Extract and return:
1. Required inputs (data types, constraints)
2. Expected outputs (data types, format)
3. Constraints (time limits, space limits, special conditions)
4. Edge cases to consider
5. Expected control flow patterns (loops, conditionals, recursion)
6. Time complexity expectations (optimal)
7. Space complexity expectations (optimal)

Return ONLY a valid JSON object:
{
  "inputs": [
    {"name": "array", "type": "int[]", "constraints": "1 <= length <= 10^5"}
  ],
  "outputs": [
    {"name": "result", "type": "int", "description": "maximum element"}
  ],
  "constraints": [
    "Array can be empty",
    "Elements can be negative",
    "Must handle duplicates"
  ],
  "edge_cases": [
    "Empty array",
    "Single element",
    "All elements same",
    "Very large array"
  ],
  "expected_patterns": [
    "Linear scan",
    "Comparison operations",
    "Variable to track maximum"
  ],
  "optimal_time_complexity": "O(n)",
  "optimal_space_complexity": "O(1)",
  "difficulty": "Easy"
}"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"{system_prompt}\n\nProblem Statement:\n{problem_statement}"
    response = model.generate_content(prompt)
    print("Problem analysis response:", response.text)
    
    result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
    return result
