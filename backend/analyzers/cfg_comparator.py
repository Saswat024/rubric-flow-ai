import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from typing import Dict
from .cfg_generator import CFG, cfg_to_dict

load_dotenv(override=True)
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")
genai.configure(api_key=api_key)


async def compare_cfgs(cfg1: CFG, cfg2: CFG, problem_analysis: dict) -> dict:
    """Compare two CFGs and determine which solution is better"""
    
    # Calculate basic structural metrics
    structural_metrics = {
        'cfg1': {
            'num_nodes': len(cfg1.nodes),
            'num_edges': len(cfg1.edges),
            'complexity': cfg1.complexity,
            'num_paths': cfg1.num_paths,
            'nesting_depth': cfg1.nesting_depth
        },
        'cfg2': {
            'num_nodes': len(cfg2.nodes),
            'num_edges': len(cfg2.edges),
            'complexity': cfg2.complexity,
            'num_paths': cfg2.num_paths,
            'nesting_depth': cfg2.nesting_depth
        }
    }
    
    system_prompt = """You are an expert algorithm evaluator. Compare two solutions (represented as Control Flow Graphs) for the given problem.

Scoring Criteria (total 100 points):
1. Correctness (40 points): Does the solution solve the problem correctly?
2. Efficiency (30 points): Time and space complexity compared to optimal
3. Code Quality (15 points): Simplicity, clarity, structure
4. Edge Cases (15 points): Handles all edge cases properly

Analyze the CFGs and structural metrics to determine:
- Which solution has better time complexity
- Which solution has better space complexity (based on nesting, recursion)
- Which solution is simpler and clearer
- Which solution handles edge cases better
- Overall winner

Return ONLY a valid JSON object:
{
  "winner": "solution1" | "solution2" | "tie",
  "solution1_score": 85,
  "solution2_score": 72,
  "comparison": {
    "correctness": {
      "solution1": {"score": 38, "feedback": "Correctly implements linear scan"},
      "solution2": {"score": 40, "feedback": "Correctly implements but with sorting"}
    },
    "efficiency": {
      "solution1": {"score": 30, "time_complexity": "O(n)", "space_complexity": "O(1)", "feedback": "Optimal approach"},
      "solution2": {"score": 20, "time_complexity": "O(n log n)", "space_complexity": "O(1)", "feedback": "Sorting is unnecessary"}
    },
    "code_quality": {
      "solution1": {"score": 14, "feedback": "Simple and clean"},
      "solution2": {"score": 10, "feedback": "Overly complex for the task"}
    },
    "edge_cases": {
      "solution1": {"score": 15, "feedback": "Handles all edge cases"},
      "solution2": {"score": 15, "feedback": "Handles all edge cases"}
    }
  },
  "overall_analysis": "Solution 1 is better because it achieves optimal O(n) time complexity with a simpler approach, while Solution 2 unnecessarily sorts the array resulting in O(n log n) complexity.",
  "recommendations": {
    "solution1": ["Consider adding input validation"],
    "solution2": ["Remove sorting step", "Use simple linear scan instead"]
  }
}"""

    cfg1_dict = cfg_to_dict(cfg1)
    cfg2_dict = cfg_to_dict(cfg2)
    
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""{system_prompt}

Problem Analysis:
{json.dumps(problem_analysis, indent=2)}

Solution 1 CFG:
{json.dumps(cfg1_dict, indent=2)}

Solution 2 CFG:
{json.dumps(cfg2_dict, indent=2)}

Structural Metrics:
{json.dumps(structural_metrics, indent=2)}

Compare these solutions and determine which is better."""

    response = model.generate_content(prompt)
    print("Comparison response:", response.text)
    
    result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
    return result
