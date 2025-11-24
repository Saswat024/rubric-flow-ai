"""
Analyzers module for CFG generation, comparison, and validation.

This module contains tools for:
- Generating Control Flow Graphs from pseudocode and flowcharts
- Canonicalizing CFGs to base-level representations
- Comparing CFGs for structural similarity
- Validating solution relevance to problem statements
- Visualizing CFGs as Mermaid diagrams
"""

from .cfg_generator import pseudocode_to_cfg, flowchart_to_cfg, cfg_to_dict, CFG, CFGNode
from .cfg_canonicalizer import canonicalize_cfg, calculate_cfg_similarity
from .cfg_comparator import compare_cfgs
from .cfg_visualizer import cfg_to_mermaid
from .problem_analyzer import analyze_problem
from .solution_validator import validate_solution_relevance

__all__ = [
    'pseudocode_to_cfg',
    'flowchart_to_cfg',
    'cfg_to_dict',
    'CFG',
    'CFGNode',
    'canonicalize_cfg',
    'calculate_cfg_similarity',
    'compare_cfgs',
    'cfg_to_mermaid',
    'analyze_problem',
    'validate_solution_relevance',
]
