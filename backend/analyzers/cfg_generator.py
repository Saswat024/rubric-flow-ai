import google.generativeai as genai
import base64, json
from PIL import Image
from io import BytesIO
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from . import config
from . import utils
from . import prompts

genai.configure(api_key=config.GOOGLE_API_KEY)


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

    try:
        model = genai.GenerativeModel(config.GEMINI_MODEL)
        prompt = f"{prompts.PSEUDOCODE_TO_CFG_PROMPT}\n\nPseudocode:\n{pseudocode}"
        response = model.generate_content(prompt)
        print("CFG from pseudocode response:", response.text)

        # Clean and parse response
        result = utils.parse_json_response(response.text)

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

    try:
        # Decode base64 image
        image_data = base64_image.split(",")[1] if "," in base64_image else base64_image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))

        model = genai.GenerativeModel(config.GEMINI_MODEL)
        response = model.generate_content([prompts.FLOWCHART_TO_CFG_PROMPT, image])
        print("CFG from flowchart response:", response.text)

        # Clean and parse response
        result = utils.parse_json_response(response.text)

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
