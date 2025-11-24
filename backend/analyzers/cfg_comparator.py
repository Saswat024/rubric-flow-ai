import google.generativeai as genai
import json
from typing import Dict
from .cfg_generator import CFG, cfg_to_dict
from . import config
from . import utils
from . import prompts

genai.configure(api_key=config.GOOGLE_API_KEY)


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
    
    system_prompt = prompts.COMPARE_CFGS_PROMPT

    cfg1_dict = cfg_to_dict(cfg1)
    cfg2_dict = cfg_to_dict(cfg2)
    
    model = genai.GenerativeModel(config.GEMINI_MODEL)
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
    
    result = utils.parse_json_response(response.text)
    return result
