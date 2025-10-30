# Problem-Solution Database System

## Overview
This system transforms the solution comparison platform into an intelligent problem-solution database that generates and stores **bottom-line Control Flow Graphs (CFGs)** - canonical, optimized representations of problem solutions.

## Key Features

### 1. Problem Management
- Upload problem statements
- Automatic duplicate detection using fuzzy matching (85% similarity threshold)
- Problem normalization and hashing for consistent identification

### 2. Bottom-Line CFG
A canonical representation that:
- Abstracts implementation details
- Captures essential control structures
- Is algorithm-agnostic (works for any valid approach)
- Serves as the gold standard for evaluation

### 3. Reference Solutions
- Store one reference solution per problem
- Automatically generates bottom-line CFG from reference
- Calculates optimal time/space complexity

### 4. Solution Evaluation
- Compare student solutions against bottom-line CFG
- Structural similarity scoring (40 points)
- Control flow coverage (30 points)
- Correctness verification (20 points)
- Efficiency analysis (10 points)

## Database Schema

### `problems` Table
- `id`: Primary key
- `problem_statement`: Full problem text
- `problem_hash`: Unique hash for duplicate detection
- `bottom_line_cfg`: JSON canonical CFG
- `optimal_time_complexity`: e.g., "O(n)"
- `optimal_space_complexity`: e.g., "O(1)"
- `problem_category`: Optional categorization

### `solutions` Table
- `id`: Primary key
- `problem_id`: Foreign key to problems
- `solution_type`: "flowchart" or "pseudocode"
- `solution_content`: The actual solution
- `cfg_json`: Generated CFG
- `evaluation_score`: 0-100 score
- `evaluation_result`: Detailed evaluation JSON
- `is_reference_solution`: Boolean flag
- `user_id`: Foreign key to users

## API Endpoints

### POST `/api/upload-problem`
Upload or find existing problem
```json
{
  "problem_statement": "Find the maximum element in an array"
}
```

### GET `/api/fetch-reference-solution/{problem_id}`
Retrieve reference solution and bottom-line CFG

### POST `/api/upload-reference-solution`
Upload reference solution (generates bottom-line CFG)
```json
{
  "problem_id": 1,
  "solution_type": "pseudocode",
  "solution_content": "..."
}
```

### POST `/api/evaluate-solution`
Evaluate user solution against bottom-line CFG
```json
{
  "problem_id": 1,
  "solution_type": "pseudocode",
  "solution_content": "..."
}
```

### GET `/api/problems`
List all problems with statistics

## Frontend Components

### ProblemUploader
- Problem statement input
- Duplicate detection display
- Status indicators

### ReferenceSelector
- Auto-fetch existing reference
- Upload new reference solution
- Display bottom-line CFG

### SolutionEvaluator
- Submit user solution
- View detailed evaluation
- See recommendations

### ProblemDatabase
- Browse all problems
- View statistics
- Filter by category

## Usage Workflow

1. **Upload Problem**: Enter problem statement
2. **Check for Duplicates**: System finds similar problems (>85% match)
3. **Upload Reference**: If new problem, upload reference solution
4. **Generate Bottom-Line CFG**: System creates canonical representation
5. **Evaluate Solutions**: Students submit solutions for evaluation
6. **View Results**: Detailed scoring and recommendations

## Navigation

- Main page: Solution Comparator (original functionality)
- `/problem-solver`: New problem database interface
- Toggle between modes using navigation buttons

## Benefits

- **Reusable Knowledge Base**: Store problems once, evaluate many times
- **Consistent Evaluation**: Bottom-line CFG ensures fair comparison
- **Reduced AI Calls**: Use stored CFGs instead of regenerating
- **Learning Analytics**: Track solution quality across attempts
- **Scalable**: Grows more valuable as database expands

## Technical Details

### CFG Canonicalization
Uses Gemini AI to:
- Merge sequential nodes
- Normalize labels to generic terms
- Abstract variable names
- Simplify control structures

### Similarity Scoring
- Structural similarity: Graph matching algorithms
- Control flow coverage: Path analysis
- Correctness: Decision point verification
- Efficiency: Complexity comparison

## Future Enhancements

- Semantic search using embeddings
- Multiple reference solutions per problem
- Category-based filtering
- Export problem reports with analytics
- Batch evaluation for classes
