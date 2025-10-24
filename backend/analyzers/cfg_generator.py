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


async def pseudocode_to_cfg(pseudocode: str) -> CFG:
    """Convert pseudocode to CFG using Gemini AI"""
    
    system_prompt = """You are an expert in control flow analysis. Convert the provided pseudocode into a Control Flow Graph (CFG) representation.

Analyze the pseudocode and extract:
1. All control flow nodes (START, END, PROCESS, DECISION, LOOP, FUNCTION_CALL, RETURN)
2. Connections between nodes
3. Conditions on decision branches
4. Calculate cyclomatic complexity using M = E - N + 2P where E=edges, N=nodes, P=connected components (usually 1)
5. Estimate number of unique paths
6. Calculate maximum nesting depth

Return ONLY a valid JSON object in this exact format:
{
  "nodes": [
    {
      "id": "node1",
      "type": "START",
      "label": "Start",
      "next_nodes": ["node2"],
      "condition": null
    },
    {
      "id": "node2",
      "type": "DECISION",
      "label": "if x > 0",
      "next_nodes": ["node3", "node4"],
      "condition": "x > 0"
    }
  ],
  "edges": [
    {"from": "node1", "to": "node2", "label": ""},
    {"from": "node2", "to": "node3", "label": "true"},
    {"from": "node2", "to": "node4", "label": "false"}
  ],
  "complexity": 2,
  "num_paths": 2,
  "nesting_depth": 1
}

Guidelines:
- Create unique IDs for each node (node1, node2, etc.)
- For DECISION nodes, create branches for all conditions
- For LOOP nodes, create back edges
- Calculate cyclomatic complexity accurately
- Consider all possible execution paths"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"{system_prompt}\n\nPseudocode:\n{pseudocode}"
    response = model.generate_content(prompt)
    print("CFG from pseudocode response:", response.text)
    
    result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
    
    # Convert to CFG object
    nodes = [CFGNode(**node) for node in result['nodes']]
    return CFG(
        nodes=nodes,
        edges=result['edges'],
        complexity=result['complexity'],
        num_paths=result['num_paths'],
        nesting_depth=result['nesting_depth']
    )


async def flowchart_to_cfg(base64_image: str) -> CFG:
    """Convert flowchart image to CFG using Gemini vision"""
    
    system_prompt = """You are an expert in flowchart analysis and control flow graphs. Analyze the flowchart image and extract its structure as a Control Flow Graph (CFG).

Examine the flowchart and identify:
1. Start and end nodes
2. Process boxes (rectangles)
3. Decision diamonds
4. Flow arrows and their directions
5. Loop structures
6. Labels and conditions

Convert this into a CFG representation and calculate:
- Cyclomatic complexity: M = E - N + 2P (edges - nodes + 2*connected_components)
- Number of unique paths from start to end
- Maximum nesting depth

Return ONLY a valid JSON object in this exact format:
{
  "nodes": [
    {
      "id": "node1",
      "type": "START",
      "label": "Start",
      "next_nodes": ["node2"],
      "condition": null
    },
    {
      "id": "node2",
      "type": "DECISION",
      "label": "Check condition",
      "next_nodes": ["node3", "node4"],
      "condition": "condition text from diamond"
    }
  ],
  "edges": [
    {"from": "node1", "to": "node2", "label": ""},
    {"from": "node2", "to": "node3", "label": "Yes"},
    {"from": "node2", "to": "node4", "label": "No"}
  ],
  "complexity": 2,
  "num_paths": 2,
  "nesting_depth": 1
}

Node types: START, END, PROCESS, DECISION, LOOP, FUNCTION_CALL, RETURN
Be accurate with edge directions and labels."""

    # Decode base64 image
    image_data = base64_image.split(',')[1] if ',' in base64_image else base64_image
    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes))

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content([system_prompt, image])
    print("CFG from flowchart response:", response.text)
    
    result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
    
    # Convert to CFG object
    nodes = [CFGNode(**node) for node in result['nodes']]
    return CFG(
        nodes=nodes,
        edges=result['edges'],
        complexity=result['complexity'],
        num_paths=result['num_paths'],
        nesting_depth=result['nesting_depth']
    )


def cfg_to_dict(cfg: CFG) -> dict:
    """Convert CFG object to dictionary for JSON serialization"""
    return {
        'nodes': [asdict(node) for node in cfg.nodes],
        'edges': cfg.edges,
        'complexity': cfg.complexity,
        'num_paths': cfg.num_paths,
        'nesting_depth': cfg.nesting_depth
    }
