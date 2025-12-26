from .cfg_generator import CFG
from typing import Dict
import re


def sanitize_label(label: str, max_length: int = 40) -> str:
    """Sanitize label for Mermaid diagram"""
    # Remove special characters that break Mermaid syntax
    label = re.sub(r"[#*\[\]{}()<>]", "", str(label))
    # Replace quotes with apostrophes
    label = label.replace('"', "'")
    # Remove multiple spaces
    label = " ".join(label.split())
    # Truncate if too long
    if len(label) > max_length:
        label = label[: max_length - 3] + "..."
    # Return placeholder if empty
    return label.strip() if label.strip() else "Node"


def cfg_to_mermaid(cfg, title: str = "CFG") -> str:
    """Convert CFG to Mermaid diagram format"""
    try:
        # Handle different input types
        if isinstance(cfg, str):
            import json

            cfg = json.loads(cfg)

        # Extract nodes and edges
        if isinstance(cfg, dict):
            nodes = cfg.get("nodes", [])
            edges = cfg.get("edges", [])
        else:
            nodes = getattr(cfg, "nodes", [])
            edges = getattr(cfg, "edges", [])

        # Validate we have nodes
        if not nodes:
            return "graph TD\n    A[No diagram available]"

        mermaid_lines = ["graph TD"]

        # Add nodes with proper formatting
        for node in nodes:
            # Get node properties (handle both dict and object)
            if isinstance(node, dict):
                node_id = node.get("id", "unknown")
                node_type = node.get("type", "PROCESS")
                node_label = node.get("label", "")
            else:
                node_id = getattr(node, "id", "unknown")
                node_type = getattr(node, "type", "PROCESS")
                node_label = getattr(node, "label", "")

            # Sanitize label
            clean_label = sanitize_label(node_label)

            # Get shape for node type
            shape_start, shape_end = get_mermaid_shape(node_type)

            # Add node line
            mermaid_lines.append(
                f'    {node_id}{shape_start}"{clean_label}"{shape_end}'
            )

        # Identify decision nodes for labeling
        decision_nodes = set()
        for node in nodes:
            node_type = (
                node.get("type")
                if isinstance(node, dict)
                else getattr(node, "type", None)
            )
            node_id = (
                node.get("id") if isinstance(node, dict) else getattr(node, "id", None)
            )
            if node_type == "DECISION" and node_id:
                decision_nodes.add(node_id)

        # Track edges from each decision node
        edge_counts = {}

        # Add edges
        for edge in edges:
            edge_from = edge.get("from", "")
            edge_to = edge.get("to", "")
            edge_label = edge.get("label", "")

            if not edge_from or not edge_to:
                continue

            # Add labels for decision branches
            if edge_from in decision_nodes:
                # Count edges from this decision node
                count = edge_counts.get(edge_from, 0)

                # Use edge label if provided, otherwise use True/False
                if edge_label and edge_label.strip():
                    label = sanitize_label(edge_label, max_length=20)
                else:
                    label = "True" if count == 0 else "False"

                edge_counts[edge_from] = count + 1
                mermaid_lines.append(f"    {edge_from} -->|{label}| {edge_to}")
            else:
                # Regular edge without label
                mermaid_lines.append(f"    {edge_from} --> {edge_to}")

        # Add styling classes
        mermaid_lines.append(
            "    classDef startEnd fill:#10b981,stroke:#059669,color:#fff"
        )
        mermaid_lines.append(
            "    classDef decision fill:#f59e0b,stroke:#d97706,color:#fff"
        )
        mermaid_lines.append(
            "    classDef process fill:#3b82f6,stroke:#2563eb,color:#fff"
        )
        mermaid_lines.append("    classDef loop fill:#8b5cf6,stroke:#7c3aed,color:#fff")

        # Add linkStyle for edges - use light color for visibility in dark mode
        edge_count = len([e for e in edges if e.get("from") and e.get("to")])
        if edge_count > 0:
            mermaid_lines.append("linkStyle default stroke:#94a3b8,stroke-width:2px")

        # Apply styles to nodes
        for node in nodes:
            node_id = (
                node.get("id") if isinstance(node, dict) else getattr(node, "id", None)
            )
            node_type = (
                node.get("type")
                if isinstance(node, dict)
                else getattr(node, "type", "PROCESS")
            )

            if not node_id:
                continue

            if node_type in ["START", "END"]:
                mermaid_lines.append(f"    class {node_id} startEnd")
            elif node_type == "DECISION":
                mermaid_lines.append(f"    class {node_id} decision")
            elif node_type == "LOOP":
                mermaid_lines.append(f"    class {node_id} loop")
            else:
                mermaid_lines.append(f"    class {node_id} process")

        return "\n".join(mermaid_lines)

    except Exception as e:
        print(f"Error in cfg_to_mermaid: {str(e)}")
        import traceback

        traceback.print_exc()
        return "graph TD\n    A[Error generating diagram]"


def get_mermaid_shape(node_type: str) -> tuple:
    """Get Mermaid shape syntax for node type"""
    shapes = {
        "START": ("([", "])"),  # Stadium shape
        "END": ("([", "])"),  # Stadium shape
        "PROCESS": ("[", "]"),  # Rectangle
        "DECISION": ("{", "}"),  # Diamond
        "LOOP": ("[[", "]]"),  # Subroutine shape
        "FUNCTION_CALL": ("[", "]"),
        "RETURN": ("[", "]"),
    }
    return shapes.get(str(node_type).upper(), ("[", "]"))


def cfg_to_dot(cfg: CFG) -> str:
    """Convert CFG to DOT format (GraphViz)"""

    dot_lines = ["digraph CFG {"]
    dot_lines.append("    rankdir=TB;")
    dot_lines.append('    node [fontname="Arial"];')

    # Add nodes
    for node in cfg.nodes:
        shape = get_dot_shape(node.type)
        color = get_dot_color(node.type)
        label = node.label.replace('"', '\\"')
        dot_lines.append(
            f'    {node.id} [label="{label}", shape={shape}, style=filled, fillcolor="{color}"];'
        )

    # Add edges
    for edge in cfg.edges:
        label = edge.get("label", "")
        if label:
            dot_lines.append(f'    {edge["from"]} -> {edge["to"]} [label="{label}"];')
        else:
            dot_lines.append(f"    {edge['from']} -> {edge['to']};")

    dot_lines.append("}")
    return "\n".join(dot_lines)


def get_dot_shape(node_type: str) -> str:
    """Get DOT shape for node type"""
    shapes = {
        "START": "ellipse",
        "END": "ellipse",
        "PROCESS": "box",
        "DECISION": "diamond",
        "LOOP": "box",
        "FUNCTION_CALL": "box",
        "RETURN": "box",
    }
    return shapes.get(node_type, "box")


def get_dot_color(node_type: str) -> str:
    """Get color for node type"""
    colors = {
        "START": "#10b981",
        "END": "#10b981",
        "PROCESS": "#3b82f6",
        "DECISION": "#f59e0b",
        "LOOP": "#8b5cf6",
        "FUNCTION_CALL": "#06b6d4",
        "RETURN": "#ec4899",
    }
    return colors.get(node_type, "#6b7280")
