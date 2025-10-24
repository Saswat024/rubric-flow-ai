from .cfg_generator import CFG
from typing import Dict


def cfg_to_mermaid(cfg: CFG, title: str = "CFG") -> str:
    """Convert CFG to Mermaid diagram format"""
    
    mermaid_lines = [f"graph TD"]
    
    # Add nodes
    for node in cfg.nodes:
        node_shape = get_mermaid_shape(node.type)
        label = node.label.replace('"', "'")
        mermaid_lines.append(f"    {node.id}{node_shape[0]}\"{label}\"{node_shape[1]}")
    
    # Add edges
    for edge in cfg.edges:
        label = edge.get('label', '')
        if label:
            mermaid_lines.append(f"    {edge['from']} -->|{label}| {edge['to']}")
        else:
            mermaid_lines.append(f"    {edge['from']} --> {edge['to']}")
    
    # Add styling
    mermaid_lines.append("    classDef startEnd fill:#10b981,stroke:#059669,color:#fff")
    mermaid_lines.append("    classDef decision fill:#f59e0b,stroke:#d97706,color:#fff")
    mermaid_lines.append("    classDef process fill:#3b82f6,stroke:#2563eb,color:#fff")
    
    # Apply styles
    for node in cfg.nodes:
        if node.type in ["START", "END"]:
            mermaid_lines.append(f"    class {node.id} startEnd")
        elif node.type == "DECISION":
            mermaid_lines.append(f"    class {node.id} decision")
        else:
            mermaid_lines.append(f"    class {node.id} process")
    
    return "\n".join(mermaid_lines)


def get_mermaid_shape(node_type: str) -> tuple:
    """Get Mermaid shape syntax for node type"""
    shapes = {
        "START": ("([", "])"),
        "END": ("([", "])"),
        "PROCESS": ("[", "]"),
        "DECISION": ("{", "}"),
        "LOOP": ("[[", "]]"),
        "FUNCTION_CALL": ("[", "]"),
        "RETURN": ("[", "]")
    }
    return shapes.get(node_type, ("[", "]"))


def cfg_to_dot(cfg: CFG) -> str:
    """Convert CFG to DOT format (GraphViz)"""
    
    dot_lines = ["digraph CFG {"]
    dot_lines.append("    rankdir=TB;")
    dot_lines.append("    node [fontname=\"Arial\"];")
    
    # Add nodes
    for node in cfg.nodes:
        shape = get_dot_shape(node.type)
        color = get_dot_color(node.type)
        label = node.label.replace('"', '\\"')
        dot_lines.append(f'    {node.id} [label="{label}", shape={shape}, style=filled, fillcolor="{color}"];')
    
    # Add edges
    for edge in cfg.edges:
        label = edge.get('label', '')
        if label:
            dot_lines.append(f'    {edge["from"]} -> {edge["to"]} [label="{label}"];')
        else:
            dot_lines.append(f'    {edge["from"]} -> {edge["to"]};')
    
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
        "RETURN": "box"
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
        "RETURN": "#ec4899"
    }
    return colors.get(node_type, "#6b7280")
