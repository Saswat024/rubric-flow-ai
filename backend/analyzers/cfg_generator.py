import google.generativeai as genai
import os
import json
import base64
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

load_dotenv(override=True)
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")
genai.configure(api_key=api_key)


@dataclass
class CFGNode:
    """Represents a node in the Control Flow Graph"""

    id: str
    type: str  # START, END, PROCESS, DECISION, LOOP, FUNCTION_CALL, RETURN
    label: str
    next_nodes: List[str]  # IDs of next nodes
    condition: Optional[str] = None  # For DECISION nodes


@dataclass
class CFG:
    """Represents a Control Flow Graph"""

    nodes: List[CFGNode]
    edges: List[Dict[str, str]]  # [{from: id, to: id, label: condition}]
    complexity: int  # Cyclomatic complexity
    num_paths: int  # Number of paths through the graph
    nesting_depth: int  # Maximum nesting depth


def validate_cfg(cfg_data: dict) -> dict:
    """Validate and fix common CFG structure issues"""
    # Ensure required fields exist
    if "nodes" not in cfg_data:
        cfg_data["nodes"] = []
    if "edges" not in cfg_data:
        cfg_data["edges"] = []
    if "complexity" not in cfg_data:
        cfg_data["complexity"] = 1
    if "num_paths" not in cfg_data:
        cfg_data["num_paths"] = 1
    if "nesting_depth" not in cfg_data:
        cfg_data["nesting_depth"] = 0

    # Validate each node has required fields
    for i, node in enumerate(cfg_data["nodes"]):
        if "id" not in node:
            node["id"] = f"node{i+1}"
        if "type" not in node:
            node["type"] = "PROCESS"
        if "label" not in node:
            node["label"] = f"Node {i+1}"
        if "next_nodes" not in node:
            node["next_nodes"] = []
        if "condition" not in node:
            node["condition"] = None

    # Validate each edge has required fields
    for edge in cfg_data["edges"]:
        if "from" not in edge:
            edge["from"] = ""
        if "to" not in edge:
            edge["to"] = ""
        if "label" not in edge:
            edge["label"] = ""

    # Remove edges with missing from/to
    cfg_data["edges"] = [e for e in cfg_data["edges"] if e.get("from") and e.get("to")]

    return cfg_data


async def pseudocode_to_cfg(pseudocode: str) -> CFG:
    """Convert pseudocode to CFG using Gemini AI"""

    system_prompt = """You are an expert in control flow analysis. Convert the provided pseudocode into a Control Flow Graph (CFG) representation.

Analyze the pseudocode carefully and extract:
1. All control flow nodes (START, END, PROCESS, DECISION, LOOP, FUNCTION_CALL, RETURN)
2. Connections between nodes in the correct logical order
3. Conditions on decision branches
4. Calculate cyclomatic complexity using M = E - N + 2P where E=edges, N=nodes, P=connected components (usually 1)
5. Estimate number of unique paths
6. Calculate maximum nesting depth

Return ONLY a valid JSON object in this exact format:
{
  "nodes": [
    {"id": "node1", "type": "START", "label": "Start", "next_nodes": ["node2"], "condition": null},
    {"id": "node2", "type": "DECISION", "label": "if x > 0", "next_nodes": ["node3", "node4"], "condition": "x > 0"},
    {"id": "node3", "type": "PROCESS", "label": "x = x + 1", "next_nodes": ["node5"], "condition": null},
    {"id": "node4", "type": "PROCESS", "label": "x = 0", "next_nodes": ["node5"], "condition": null},
    {"id": "node5", "type": "END", "label": "End", "next_nodes": [], "condition": null}
  ],
  "edges": [
    {"from": "node1", "to": "node2", "label": ""},
    {"from": "node2", "to": "node3", "label": "True"},
    {"from": "node2", "to": "node4", "label": "False"},
    {"from": "node3", "to": "node5", "label": ""},
    {"from": "node4", "to": "node5", "label": ""}
  ],
  "complexity": 2,
  "num_paths": 2,
  "nesting_depth": 1
}

CRITICAL RULES:
- Create unique sequential IDs (node1, node2, node3, ...)
- Every CFG must have exactly ONE START node and at least ONE END node
- DECISION nodes must have exactly 2 branches: one labeled "True" and one "False"
- For IF statements: True branch executes the IF body, False branch skips to next statement
- For IF-ELSE statements: True branch is IF body, False branch is ELSE body
- For LOOP nodes (while, for): True branch continues loop body, False branch exits loop
- PROCESS nodes represent assignments, calculations, print statements, or operations
- Each RETURN statement should be a RETURN type node that connects to END
- All execution paths must eventually reach an END node
- Sequential statements flow linearly: node1 → node2 → node3
- Nested structures (loops inside ifs, etc.) increase nesting_depth
- Calculate cyclomatic complexity: M = E - N + 2 (E=number of edges, N=number of nodes)
- Count all possible execution paths from START to END carefully
- Use descriptive labels that summarize what each node does
- Keep labels concise but informative (under 50 characters)

Common Patterns:
1. Simple IF: START → DECISION → [True: PROCESS → END, False: END]
2. IF-ELSE: START → DECISION → [True: PROCESS_A → END, False: PROCESS_B → END]
3. WHILE loop: START → LOOP_DECISION → [True: PROCESS → back to LOOP_DECISION, False: END]
4. Sequential: START → PROCESS1 → PROCESS2 → PROCESS3 → END"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"{system_prompt}\n\nPseudocode:\n{pseudocode}"
        response = model.generate_content(prompt)
        print("CFG from pseudocode response:", response.text)

        # Clean and parse response
        response_text = response.text.strip()
        response_text = response_text.replace("```json", "").replace("```", "").strip()

        result = json.loads(response_text)

        # Validate and fix structure
        result = validate_cfg(result)

        # Convert to CFG object
        nodes = [CFGNode(**node) for node in result["nodes"]]
        return CFG(
            nodes=nodes,
            edges=result["edges"],
            complexity=result["complexity"],
            num_paths=result["num_paths"],
            nesting_depth=result["nesting_depth"],
        )
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response text: {response.text}")
        # Return a minimal valid CFG
        return CFG(
            nodes=[
                CFGNode(
                    id="node1",
                    type="START",
                    label="Start",
                    next_nodes=["node2"],
                    condition=None,
                ),
                CFGNode(
                    id="node2",
                    type="PROCESS",
                    label="Error parsing pseudocode",
                    next_nodes=["node3"],
                    condition=None,
                ),
                CFGNode(
                    id="node3", type="END", label="End", next_nodes=[], condition=None
                ),
            ],
            edges=[
                {"from": "node1", "to": "node2", "label": ""},
                {"from": "node2", "to": "node3", "label": ""},
            ],
            complexity=1,
            num_paths=1,
            nesting_depth=0,
        )
    except Exception as e:
        print(f"Error in pseudocode_to_cfg: {e}")
        import traceback

        traceback.print_exc()
        raise


async def flowchart_to_cfg(base64_image: str) -> CFG:
    """Convert flowchart image to CFG using Gemini vision"""

    system_prompt = """You are an expert in flowchart analysis and control flow graphs. Analyze the flowchart image and extract its structure as a Control Flow Graph (CFG).

Examine the flowchart image carefully and identify:
1. Start nodes - typically rounded rectangles/ovals at the top labeled "Start" or "Begin"
2. End nodes - typically rounded rectangles/ovals labeled "End" or "Stop"
3. Process boxes - rectangles containing operations, assignments, or calculations
4. Decision diamonds - containing questions or conditions with Yes/No or True/False branches
5. Flow arrows - trace the direction carefully, especially which way is True/False
6. Loop structures - arrows that point backward in the flow
7. All text labels on shapes and arrows

Convert this into a CFG representation and calculate metrics:
- Cyclomatic complexity: M = E - N + 2 (E=edges, N=nodes, 2=constant)
- Number of unique paths from START to END
- Maximum nesting depth (deepest level of nested structures)

Return ONLY a valid JSON object in this exact format:
{
  "nodes": [
    {"id": "node1", "type": "START", "label": "Start", "next_nodes": ["node2"], "condition": null},
    {"id": "node2", "type": "DECISION", "label": "x > 0?", "next_nodes": ["node3", "node4"], "condition": "x > 0"},
    {"id": "node3", "type": "PROCESS", "label": "result = x * 2", "next_nodes": ["node5"], "condition": null},
    {"id": "node4", "type": "PROCESS", "label": "result = 0", "next_nodes": ["node5"], "condition": null},
    {"id": "node5", "type": "END", "label": "End", "next_nodes": [], "condition": null}
  ],
  "edges": [
    {"from": "node1", "to": "node2", "label": ""},
    {"from": "node2", "to": "node3", "label": "True"},
    {"from": "node2", "to": "node4", "label": "False"},
    {"from": "node3", "to": "node5", "label": ""},
    {"from": "node4", "to": "node5", "label": ""}
  ],
  "complexity": 2,
  "num_paths": 2,
  "nesting_depth": 1
}

CRITICAL RULES:
- Assign unique sequential IDs: node1, node2, node3, ...
- Follow arrow directions exactly as shown in the flowchart
- Every CFG must have ONE START and at least ONE END node
- DECISION nodes (diamond shapes) must have exactly 2 outgoing edges
- Label decision branches as "True" and "False" based on arrow labels (Yes=True, No=False)
- If arrow labels say "Yes/No", convert to "True/False"
- PROCESS nodes are rectangles with operations or assignments
- Extract the exact text from each shape as the label
- If text is unclear, describe what the shape appears to represent
- Trace each arrow path completely - don't miss any connections
- If a loop exists (arrow pointing upward/backward), the target node should be type "LOOP"
- Count nodes and edges accurately for complexity: M = E - N + 2
- Node type must be one of: START, END, PROCESS, DECISION, LOOP, FUNCTION_CALL, RETURN
- Ensure every execution path eventually reaches an END node
- Keep labels under 50 characters, summarize if needed

Visual Identification Guide:
- Ovals/Rounded rectangles = START or END
- Rectangles = PROCESS
- Diamonds = DECISION
- Arrows = edges (connections between nodes)
- Text on arrows = edge labels
- Text inside shapes = node labels"""

    try:
        # Decode base64 image
        image_data = base64_image.split(",")[1] if "," in base64_image else base64_image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content([system_prompt, image])
        print("CFG from flowchart response:", response.text)

        # Clean and parse response
        response_text = response.text.strip()
        response_text = response_text.replace("```json", "").replace("```", "").strip()

        result = json.loads(response_text)

        # Validate and fix structure
        result = validate_cfg(result)

        # Convert to CFG object
        nodes = [CFGNode(**node) for node in result["nodes"]]
        return CFG(
            nodes=nodes,
            edges=result["edges"],
            complexity=result["complexity"],
            num_paths=result["num_paths"],
            nesting_depth=result["nesting_depth"],
        )
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response text: {response.text}")
        # Return a minimal valid CFG
        return CFG(
            nodes=[
                CFGNode(
                    id="node1",
                    type="START",
                    label="Start",
                    next_nodes=["node2"],
                    condition=None,
                ),
                CFGNode(
                    id="node2",
                    type="PROCESS",
                    label="Error parsing flowchart",
                    next_nodes=["node3"],
                    condition=None,
                ),
                CFGNode(
                    id="node3", type="END", label="End", next_nodes=[], condition=None
                ),
            ],
            edges=[
                {"from": "node1", "to": "node2", "label": ""},
                {"from": "node2", "to": "node3", "label": ""},
            ],
            complexity=1,
            num_paths=1,
            nesting_depth=0,
        )
    except Exception as e:
        print(f"Error in flowchart_to_cfg: {e}")
        import traceback

        traceback.print_exc()
        raise


def cfg_to_dict(cfg: CFG) -> dict:
    """Convert CFG object to dictionary for JSON serialization"""
    return {
        "nodes": [asdict(node) for node in cfg.nodes],
        "edges": cfg.edges,
        "complexity": cfg.complexity,
        "num_paths": cfg.num_paths,
        "nesting_depth": cfg.nesting_depth,
    }
