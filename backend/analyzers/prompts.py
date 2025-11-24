PSEUDOCODE_TO_CFG_PROMPT = """You are an expert in control flow analysis. Convert the provided pseudocode into a Control Flow Graph (CFG) representation.

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

FLOWCHART_TO_CFG_PROMPT = """You are an expert in flowchart analysis and control flow graphs. Analyze the flowchart image and extract its structure as a Control Flow Graph (CFG).

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

CANONICALIZE_CFG_PROMPT = """You are an expert algorithm analyst. Generate a canonical, base-level Control Flow Graph (CFG) that represents the fundamental logic for solving this problem.

The base-level CFG should:
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

CALCULATE_SIMILARITY_PROMPT = """You are an expert in algorithm analysis and control flow comparison. Compare the user's CFG against the reference canonical (base-level) CFG to evaluate how well the user's solution captures the essential algorithmic structure.

CRITICAL FIRST STEP - Problem Relevance Check:
BEFORE evaluating structural similarity, you MUST verify that the user's solution actually attempts to solve the stated problem.
- Examine the node labels, operations, and logic flow in the user's CFG
- Check if the algorithm's purpose matches the problem statement
- If the user submitted a solution for a DIFFERENT problem (e.g., GCD when asked for factorial, sorting when asked for search), immediately assign:
  * total_score: 0
  * All category scores: 0
  * Add to differences: "CRITICAL: Solution solves a different problem than stated. User submitted [detected algorithm] but problem asks for [required algorithm]"
  * Stop evaluation and return the failure result

Evaluation Criteria (total 100 points) - ONLY if solution is relevant:

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

COMPARE_CFGS_PROMPT = """You are an expert algorithm evaluator. Compare two solutions (represented as Control Flow Graphs) for the given problem.

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

ANALYZE_PROBLEM_PROMPT = """You are an expert algorithm analyst. Analyze the given problem statement and extract key information that will help evaluate solutions.

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
