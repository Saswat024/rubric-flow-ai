import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from .cfg_generator import CFG, CFGNode, cfg_to_dict

load_dotenv(override=True)
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")
genai.configure(api_key=api_key)


def validate_canonical_cfg(result: dict) -> dict:
    """Validate and ensure canonical CFG has required fields"""
    if "nodes" not in result:
        result["nodes"] = []
    if "edges" not in result:
        result["edges"] = []
    if "complexity" not in result:
        result["complexity"] = 1
    if "num_paths" not in result:
        result["num_paths"] = 1
    if "nesting_depth" not in result:
        result["nesting_depth"] = 0
    if "time_complexity" not in result:
        result["time_complexity"] = "O(n)"
    if "space_complexity" not in result:
        result["space_complexity"] = "O(1)"
    if "canonical_patterns" not in result:
        result["canonical_patterns"] = []

    return result


def validate_similarity_result(result: dict) -> dict:
    """Validate and ensure similarity result has required fields"""
    if "total_score" not in result:
        result["total_score"] = 0

    if "breakdown" not in result:
        result["breakdown"] = {}

    # Ensure all breakdown categories exist
    default_categories = {
        "structural_similarity": {"score": 0, "feedback": "Not evaluated"},
        "control_flow_coverage": {"score": 0, "feedback": "Not evaluated"},
        "correctness": {"score": 0, "feedback": "Not evaluated"},
        "efficiency": {"score": 0, "feedback": "Not evaluated"},
    }

    for category, default_value in default_categories.items():
        if category not in result["breakdown"]:
            result["breakdown"][category] = default_value
        elif "score" not in result["breakdown"][category]:
            result["breakdown"][category]["score"] = 0
        elif "feedback" not in result["breakdown"][category]:
            result["breakdown"][category]["feedback"] = ""

    if "differences" not in result:
        result["differences"] = []
    if "missing_paths" not in result:
        result["missing_paths"] = []
    if "extra_paths" not in result:
        result["extra_paths"] = []
    if "recommendations" not in result:
        result["recommendations"] = []

    return result


async def canonicalize_cfg(cfg: CFG, problem_statement: str) -> dict:
    """Convert CFG to canonical bottom-line representation"""

    system_prompt = """You are an expert algorithm analyst. Generate a canonical, bottom-line Control Flow Graph (CFG) that represents the fundamental logic for solving this problem.

The bottom-line CFG should:
1. Abstract away implementation details (specific variable names, exact loop types, language syntax)
2. Capture only essential control structures (key decisions, loops, sequential steps)
3. Represent the most efficient logical flow to solve the problem
4. Be algorithm-agnostic (works for recursive or iterative approaches)
5. Include only necessary decision points and critical paths
6. Merge redundant or trivial operations

Normalize all labels to generic, semantic terms:
- "initialize variables" for setup steps
- "check boundary condition" for edge case validation
- "check base case" for recursion termination
- "process element" for main operations on data
- "update accumulator" for incremental changes
- "iterate collection" for loop operations
- "return result" for final output

Simplification rules:
- Merge consecutive PROCESS nodes into single semantic operations
- Eliminate redundant decision nodes that don't affect logic
- Normalize all loop structures to generic "LOOP" type
- Abstract variable names to semantic placeholders (e.g., "input", "result", "index")
- Remove language-specific constructs
- Focus on algorithmic flow, not implementation details

Calculate accurate complexity metrics:
- Time complexity: Analyze loop nesting and recursion depth
- Space complexity: Consider auxiliary data structures and recursion stack
- Use Big-O notation (O(1), O(log n), O(n), O(n log n), O(n²), etc.)

Identify canonical patterns present:
- "linear_scan" - single pass through data
- "nested_iteration" - nested loops
- "divide_and_conquer" - recursive splitting
- "two_pointers" - dual index traversal
- "sliding_window" - fixed/variable window
- "dynamic_programming" - memoization/tabulation
- "greedy" - local optimal choices
- "backtracking" - exhaustive search with pruning

Return ONLY a valid JSON object:
{
  "nodes": [
    {"id": "node1", "type": "START", "label": "Start", "next_nodes": ["node2"], "condition": null},
    {"id": "node2", "type": "PROCESS", "label": "initialize variables", "next_nodes": ["node3"], "condition": null},
    {"id": "node3", "type": "DECISION", "label": "check boundary condition", "next_nodes": ["node4", "node5"], "condition": "is input valid"},
    {"id": "node4", "type": "RETURN", "label": "return error", "next_nodes": ["node6"], "condition": null},
    {"id": "node5", "type": "LOOP", "label": "iterate collection", "next_nodes": ["node7", "node8"], "condition": "has more elements"},
    {"id": "node7", "type": "PROCESS", "label": "process element", "next_nodes": ["node5"], "condition": null},
    {"id": "node8", "type": "RETURN", "label": "return result", "next_nodes": ["node6"], "condition": null},
    {"id": "node6", "type": "END", "label": "End", "next_nodes": [], "condition": null}
  ],
  "edges": [
    {"from": "node1", "to": "node2", "label": ""},
    {"from": "node2", "to": "node3", "label": ""},
    {"from": "node3", "to": "node4", "label": "False"},
    {"from": "node3", "to": "node5", "label": "True"},
    {"from": "node4", "to": "node6", "label": ""},
    {"from": "node5", "to": "node7", "label": "True"},
    {"from": "node5", "to": "node8", "label": "False"},
    {"from": "node7", "to": "node5", "label": ""},
    {"from": "node8", "to": "node6", "label": ""}
  ],
  "complexity": 2,
  "num_paths": 3,
  "nesting_depth": 1,
  "time_complexity": "O(n)",
  "space_complexity": "O(1)",
  "canonical_patterns": ["linear_scan", "boundary_check"]
}

CRITICAL: 
- Analyze the actual algorithm complexity, don't guess
- For loops over n elements: O(n)
- For nested loops: O(n²) or O(n*m)
- For divide-and-conquer: O(log n) or O(n log n)
- For recursion: Consider stack space in space_complexity
- Be precise with Big-O notation"""

    try:
        cfg_dict = cfg_to_dict(cfg)
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""{system_prompt}

Problem Statement:
{problem_statement}

Original CFG to Canonicalize:
{json.dumps(cfg_dict, indent=2)}

Generate the canonical bottom-line CFG that captures the essential algorithmic structure."""

        response = model.generate_content(prompt)
        print("Canonical CFG response:", response.text)

        # Clean and parse response
        response_text = response.text.strip()
        response_text = response_text.replace("```json", "").replace("```", "").strip()

        result = json.loads(response_text)

        # Validate and ensure required fields
        result = validate_canonical_cfg(result)

        return result

    except json.JSONDecodeError as e:
        print(f"JSON parsing error in canonicalize_cfg: {e}")
        print(f"Response text: {response.text}")
        # Return a minimal valid canonical CFG
        return {
            "nodes": cfg_dict.get("nodes", []),
            "edges": cfg_dict.get("edges", []),
            "complexity": cfg_dict.get("complexity", 1),
            "num_paths": cfg_dict.get("num_paths", 1),
            "nesting_depth": cfg_dict.get("nesting_depth", 0),
            "time_complexity": "O(n)",
            "space_complexity": "O(1)",
            "canonical_patterns": ["unknown"],
        }
    except Exception as e:
        print(f"Error in canonicalize_cfg: {e}")
        import traceback

        traceback.print_exc()
        raise


async def calculate_cfg_similarity(user_cfg: dict, reference_cfg: dict) -> dict:
    """Calculate structural similarity between user CFG and reference CFG"""

    system_prompt = """You are an expert in algorithm analysis and control flow comparison. Compare the user's CFG against the reference canonical (bottom-line) CFG to evaluate how well the user's solution captures the essential algorithmic structure.

Evaluation Criteria (total 100 points):

1. Structural Similarity (40 points):
   - Does the control flow structure match the essential pattern?
   - Are decision points in the correct logical order?
   - Are loops and branches properly structured?
   - Is the overall flow logical and correct?
   Award: 40 (perfect match), 30-39 (minor differences), 20-29 (some issues), 0-19 (major structural problems)

2. Control Flow Coverage (30 points):
   - Are all necessary execution paths present?
   - Are edge cases and boundary conditions handled?
   - Are all critical decision points included?
   - Is the solution complete?
   Award: 30 (all paths covered), 20-29 (minor gaps), 10-19 (missing paths), 0-9 (incomplete)

3. Correctness (20 points):
   - Are decision conditions logically correct?
   - Do branches lead to correct next steps?
   - Is the logic sound and bug-free?
   - Would this translate to working code?
   Award: 20 (fully correct), 15-19 (minor issues), 10-14 (some errors), 0-9 (major logic errors)

4. Efficiency (10 points):
   - Are there unnecessary loops or redundant operations?
   - Is the complexity optimal for the problem?
   - Are there wasteful branches or duplicate checks?
   - Could the flow be simplified?
   Award: 10 (optimal), 7-9 (minor inefficiency), 4-6 (some waste), 0-3 (very inefficient)

Comparison Guidelines:
- Focus on algorithmic similarity, not implementation details
- User may use different variable names or node labels - that's OK
- Look for matching control structures (loops, conditions, sequences)
- Check if execution paths achieve the same logical outcome
- Identify genuinely missing critical paths vs. implementation variations
- Note unnecessary complexity that doesn't add value

Return ONLY a valid JSON object:
{
  "total_score": 85,
  "breakdown": {
    "structural_similarity": {
      "score": 35,
      "feedback": "Control flow matches well with minor ordering differences in boundary checks"
    },
    "control_flow_coverage": {
      "score": 28,
      "feedback": "Most paths present but missing edge case for empty input"
    },
    "correctness": {
      "score": 18,
      "feedback": "Logic is sound with correct decision points and proper branching"
    },
    "efficiency": {
      "score": 9,
      "feedback": "Slightly redundant validation step that could be merged"
    }
  },
  "differences": [
    "User has extra initialization step for variable tracking",
    "Loop condition is equivalent but phrased differently"
  ],
  "missing_paths": [
    "Missing explicit check for empty input before processing",
    "No path for handling null/undefined values"
  ],
  "extra_paths": [
    "Redundant validation of already-checked condition",
    "Unnecessary intermediate result variable"
  ],
  "recommendations": [
    "Add boundary check at start for empty/null input",
    "Consider merging initialization and first validation step",
    "Remove duplicate condition check in loop body"
  ]
}

IMPORTANT:
- Be fair and understanding of different valid approaches
- Don't penalize style differences or equivalent logic
- Focus on genuine logical differences that affect correctness or efficiency
- Provide constructive, actionable feedback
- If user's approach is different but equally valid, give full credit"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""{system_prompt}

Reference CFG (canonical bottom-line):
{json.dumps(reference_cfg, indent=2)}

User's CFG:
{json.dumps(user_cfg, indent=2)}

Evaluate how well the user's solution matches the canonical structure."""

        response = model.generate_content(prompt)
        print("Similarity calculation response:", response.text)

        # Clean and parse response
        response_text = response.text.strip()
        response_text = response_text.replace("```json", "").replace("```", "").strip()

        result = json.loads(response_text)

        # Validate and ensure required fields
        result = validate_similarity_result(result)

        return result

    except json.JSONDecodeError as e:
        print(f"JSON parsing error in calculate_cfg_similarity: {e}")
        print(f"Response text: {response.text}")
        # Return a default similarity result
        return {
            "total_score": 50,
            "breakdown": {
                "structural_similarity": {
                    "score": 20,
                    "feedback": "Unable to evaluate due to parsing error",
                },
                "control_flow_coverage": {
                    "score": 15,
                    "feedback": "Unable to evaluate due to parsing error",
                },
                "correctness": {
                    "score": 10,
                    "feedback": "Unable to evaluate due to parsing error",
                },
                "efficiency": {
                    "score": 5,
                    "feedback": "Unable to evaluate due to parsing error",
                },
            },
            "differences": ["Evaluation incomplete due to technical error"],
            "missing_paths": [],
            "extra_paths": [],
            "recommendations": ["Please try submitting again"],
        }
    except Exception as e:
        print(f"Error in calculate_cfg_similarity: {e}")
        import traceback

        traceback.print_exc()
        raise
